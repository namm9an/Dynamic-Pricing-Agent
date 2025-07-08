"""
Model optimization script for converting PyTorch models to ONNX format
and performing quantization for faster inference.
"""
import os
import time
import torch
import onnx
import onnxruntime as ort
import numpy as np
from pathlib import Path
from typing import Dict, Any, Tuple
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelOptimizer:
    """Handles model conversion and optimization"""
    
    def __init__(self, model_path: str = "./models"):
        self.model_path = Path(model_path)
        self.optimized_path = self.model_path / "optimized"
        self.optimized_path.mkdir(exist_ok=True)
        
    def convert_to_onnx(self, model, input_shape: Tuple[int, ...], 
                       output_path: str, dynamic_axes: Dict[str, Dict[int, str]] = None) -> bool:
        """Convert PyTorch model to ONNX format"""
        try:
            # Create dummy input
            dummy_input = torch.randn(*input_shape)
            
            # Export to ONNX
            torch.onnx.export(
                model,
                dummy_input,
                output_path,
                export_params=True,
                opset_version=11,
                do_constant_folding=True,
                input_names=['input'],
                output_names=['output'],
                dynamic_axes=dynamic_axes or {'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
            )
            
            # Verify the model
            onnx_model = onnx.load(output_path)
            onnx.checker.check_model(onnx_model)
            
            logger.info(f"Successfully converted model to ONNX: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to convert model to ONNX: {e}")
            return False
    
    def quantize_model(self, onnx_path: str, quantized_path: str) -> bool:
        """Quantize ONNX model to INT8 for faster inference"""
        try:
            from onnxruntime.quantization import quantize_dynamic, QuantType
            
            quantize_dynamic(
                model_input=onnx_path,
                model_output=quantized_path,
                weight_type=QuantType.QInt8,
                extra_options={'WeightSymmetric': False}
            )
            
            logger.info(f"Successfully quantized model: {quantized_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to quantize model: {e}")
            return False
    
    def benchmark_model(self, model_path: str, input_shape: Tuple[int, ...], 
                       num_runs: int = 100) -> Dict[str, float]:
        """Benchmark model inference performance"""
        try:
            # Create inference session
            session = ort.InferenceSession(model_path)
            
            # Prepare input
            input_name = session.get_inputs()[0].name
            dummy_input = np.random.randn(*input_shape).astype(np.float32)
            
            # Warm up
            for _ in range(10):
                session.run(None, {input_name: dummy_input})
            
            # Benchmark
            times = []
            for _ in range(num_runs):
                start = time.time()
                session.run(None, {input_name: dummy_input})
                times.append(time.time() - start)
            
            return {
                'mean_time': np.mean(times),
                'std_time': np.std(times),
                'min_time': np.min(times),
                'max_time': np.max(times),
                'p95_time': np.percentile(times, 95),
                'throughput': 1.0 / np.mean(times)
            }
            
        except Exception as e:
            logger.error(f"Failed to benchmark model: {e}")
            return {}
    
    def optimize_demand_model(self) -> Dict[str, Any]:
        """Optimize the demand prediction model"""
        results = {}
        
        try:
            # Load the original PyTorch model
            model_path = self.model_path / "pytorch_model.bin"
            if not model_path.exists():
                logger.warning("PyTorch model not found, skipping optimization")
                return {"status": "skipped", "reason": "Model not found"}
            
            # For this example, we'll create a simple model structure
            # In production, load your actual model
            from backend.pricing_engine.demand_model import DemandModel
            model = DemandModel()
            model.eval()
            
            # Define input shape (batch_size, sequence_length, features)
            input_shape = (1, 7, 4)  # 7 days of history, 4 features
            
            # Convert to ONNX
            onnx_path = str(self.optimized_path / "demand_model.onnx")
            if self.convert_to_onnx(model, input_shape, onnx_path):
                results['onnx_conversion'] = 'success'
                
                # Benchmark original ONNX model
                results['onnx_benchmark'] = self.benchmark_model(onnx_path, input_shape)
                
                # Quantize model
                quantized_path = str(self.optimized_path / "demand_model_quantized.onnx")
                if self.quantize_model(onnx_path, quantized_path):
                    results['quantization'] = 'success'
                    
                    # Benchmark quantized model
                    results['quantized_benchmark'] = self.benchmark_model(quantized_path, input_shape)
                    
                    # Calculate speedup
                    if results.get('onnx_benchmark') and results.get('quantized_benchmark'):
                        speedup = results['onnx_benchmark']['mean_time'] / results['quantized_benchmark']['mean_time']
                        results['speedup'] = speedup
                        logger.info(f"Quantization achieved {speedup:.2f}x speedup")
            
        except Exception as e:
            logger.error(f"Failed to optimize demand model: {e}")
            results['error'] = str(e)
        
        return results
    
    def compare_accuracy(self, original_model, optimized_path: str, 
                        test_data: np.ndarray) -> Dict[str, float]:
        """Compare accuracy between original and optimized models"""
        try:
            # Get predictions from original model
            with torch.no_grad():
                original_output = original_model(torch.tensor(test_data, dtype=torch.float32))
                original_pred = original_output.numpy()
            
            # Get predictions from optimized model
            session = ort.InferenceSession(optimized_path)
            input_name = session.get_inputs()[0].name
            optimized_pred = session.run(None, {input_name: test_data.astype(np.float32)})[0]
            
            # Calculate metrics
            mse = np.mean((original_pred - optimized_pred) ** 2)
            mae = np.mean(np.abs(original_pred - optimized_pred))
            max_error = np.max(np.abs(original_pred - optimized_pred))
            
            return {
                'mse': float(mse),
                'mae': float(mae),
                'max_error': float(max_error),
                'correlation': float(np.corrcoef(original_pred.flatten(), optimized_pred.flatten())[0, 1])
            }
            
        except Exception as e:
            logger.error(f"Failed to compare accuracy: {e}")
            return {}

def main():
    """Main optimization workflow"""
    optimizer = ModelOptimizer()
    
    logger.info("Starting model optimization...")
    
    # Optimize demand model
    results = optimizer.optimize_demand_model()
    
    # Save results
    results_path = optimizer.optimized_path / "optimization_results.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Optimization complete. Results saved to {results_path}")
    
    # Print summary
    if 'speedup' in results:
        print(f"\n✅ Model optimization successful!")
        print(f"   - Speedup: {results['speedup']:.2f}x")
        print(f"   - Original latency: {results['onnx_benchmark']['mean_time']*1000:.2f}ms")
        print(f"   - Optimized latency: {results['quantized_benchmark']['mean_time']*1000:.2f}ms")
    else:
        print("\n❌ Model optimization failed. Check logs for details.")

if __name__ == "__main__":
    main()
