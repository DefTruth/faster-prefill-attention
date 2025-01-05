# 📚 FFPA: Faster Flash Prefill Attention  
📚 **[WIP]** FFPA: Yet antother Faster Flash Prefill Attention with **O(1) SRAM complexity** & **O(d/4) or O(1) register complexity** for large headdim (D > 256), almost **>1.5x** 🎉 faster than SDPA EA, both MMA acc F32 and F16 (Experimental 👀~). This project is still in its early development stages and currently provides a few experimental kernels and benchmarks for reference.

## 📖 Contents

- [📖 Prerequisites](#prerequisites)
- [📖 FFPA L1~L3 Design](#ffpa-design)
- [📖 FFPA L1 Benchmark](#L1-bench)
- [📖 FFPA L2 Benchmark](#L1-bench)
- [📖 FFPA L3 Benchmark](#L1-bench)
- [📖 Python Testing](#test)
- [📖 References](#ref)

## 📖 FFPA L1~L3: FlashAttention + MMA Fine-grained Tiling
<div id="ffpa-design"></div>  

We have extended FlashAttention for large headdim (D > 256) by implementing **Fine-grained Tiling** at the **MMA level** for the Q·K^T and P·V matmul. This approach results in a constant SRAM usage of Br * 16 or Bc * 16 for Q, K, and V, leading to an overall SRAM complexity of O(Br * 16) ≈ O(1) and a register complexity of O(d/4) or O(1). Consequently, this method allows us to extend headdim beyond 256 and achieve faster performance compared to SDPA with or without MMA Accumulation F32 (almost **>1.5x** 🎉 faster than SDPA EA). 

We have named this new attention tiling technique **FFPA: Faster Flash Prefill Attention**. We have designed three levels of FFPA based on SRAM and register complexity considerations. All levels will not introduce any additional VRAM requirements, ensuring that the GPU HBM memory complexity remains consistent with FlashAttention. (d=headdim)

- [x] 📚L1: level 1, O(Brx16)~O(1) SRAM complexity, O(d/4) register complexity.  
- [ ] 📚L2: level 2, O(Brx16)~O(1) SRAM complexity, O(1) register complexity + Q@K^T recomputation.  
- [ ] 📚L3: level 3, O(Brx16)~O(1) SRAM complexity, O(1) register complexity + scaling O via HBM offloading. 

By leveraging this approach, we can achieve improved performance for large headdim (D > 256) through a balanced utilization of FlashAttention (which is not designed to support D > 256) and SDPA EA. This allows us to take advantage of the strengths of both methods while mitigating their limitations. 

## 📖 Prerequisites
<div id="prerequisites"></div>  

- PyTorch >= 2.4.0, CUDA >= 12.0
- Recommended: PyTorch 2.5.1, CUDA 12.5

## 📖 FFPA L1 (Level 1): Benchmark 🎉🎉

<div id="L1-bench"></div>  

L1: level 1, O(Brx16)~O(1) SRAM complexity, O(d/4) register complexity, the same GPU HBM memory complexity as FlashAttention. B=1, H=48, N=8192, D=320-1024(FA2 not supported). More benchmark data will be added over time as the project continues to develop. (Notes, *=MMA Acc F32, **=MMA Acc F16, Softmax Acc is always F32, T=TFLOPS, 👇Benchmark)

- 📚 NVIDIA RTX 3080 Laptop

|Algorithm|320|384|448|512|576|640|704|768|832|896|960|1024|    
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|  
|SDPA EA|13T|16T|12T|16T|15T|15T|15T|15T|15T|15T|15T|15T|  
|FFPA L1*|32T|30T|30T|28T|28T|27T|26T|25T|25T|25T|25T|24T|   
|Speedup|2.48x|1.88x|2.55x|1.75x|1.90x|1.77x|1.73x|1.67x|1.66x|1.66x|1.66x|1.54x|  
|FFPA L1**|40T|38T|39T|36T|35T|34T|33T|32T|31T|31T|28T|27T|  
|Speedup|3.07x|2.42x|3.33x|2.24x|2.35x|2.19x|2.19x|2.13x|2.03x|2.03x|1.90x|1.74x|

## 📖 Python Testing 
<div id="test"></div>  

You can test many custom FFPA kernel via Python script and figure out the difference in their performance.
```bash
# You can test Ada or Ampere only, also, Volta, Ampere, Ada, Hopper, ...
export TORCH_CUDA_ARCH_LIST=Ada # for Ada only
export TORCH_CUDA_ARCH_LIST=Ampere # for Ampere only
python3 ffpa.py --B 1 --H 48 --N 8192 --check --show-all --D 320 
```
log: (tested on NVIDIA RTX 3080 Laptop)
```bash
----------------------------------------------------B=1, H=48, N=8192, D=320, Warmup: 1, Iters: 5-----------------------------------------------------
                   (sdpa): ['-0.02232361 ', '0.01992798  ', '0.00818634  '], time:315.3534ms, TFLOPS:13.13 (+0.00 %) (~1.00x)
 (ffpa+acc+f32+L1+stage1): ['-0.02232361 ', '0.01991272  ', '0.00817108  '], time:152.9723ms, TFLOPS:27.06 (+106.15%)(~2.06x)
 (ffpa+acc+f32+L1+stage2): ['-0.02232361 ', '0.01991272  ', '0.00817108  '], time:127.2879ms, TFLOPS:32.52 (+20.18%) (~2.48x)
 (ffpa+acc+f16+L1+stage1): ['-0.02238464 ', '0.01992798  ', '0.00816345  '], time:121.3927ms, TFLOPS:34.10 (+4.86 %) (~2.60x)
 (ffpa+acc+f16+L1+stage2): ['-0.02238464 ', '0.01992798  ', '0.00816345  '], time:102.5883ms, TFLOPS:40.35 (+18.33%) (~3.07x)
------------------------------------------------------------------------------------------------------------------------------------------------------
```

## ©️License

<div id="License"></div>  

GNU General Public License v3.0

## 🎉Contribute 

<div id="Contribute"></div>  

How to contribute? Wecome to star this repo to support me👆🏻 ~

## ©️Citations🎉🎉

```BibTeX
@misc{faster-prefill-attention@2025,
  title={faster-prefill-attention: Yet antother Faster Flash Prefill Attention than SDPA EA for large headdim.},
  url={https://github.com/DefTruth/faster-prefill-attention},
  note={Open-source software available at https://github.com/DefTruth/faster-prefill-attention},
  author={DefTruth etc},
  year={2025}
}
```

## 📖 References   
<div id="ref"></div>  

- [flash-attention](https://github.com/Dao-AILab/flash-attention)
- [CUDA-Learn-Notes](https://github.com/DefTruth/CUDA-Learn-Notes)
- [cuda_hgemm](https://github.com/Bruce-Lee-LY/cuda_hgemm)
- [cutlass](https://github.com/NVIDIA/cutlass)
