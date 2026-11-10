---
title: Why Inference Matters 12x More Than Training
type: video
source: YC Library
url: "https://www.ycombinator.com/library/g5-why-inference-matters-12x-more-than-training"
author: Y Combinator
series: Paper Club
youtube_id: mHNKuH-9OxU
youtube_url: "https://www.youtube.com/watch?v=mHNKuH-9OxU"
upload_date: 2026-10-24
length: "1:50:48"
views: 68972
has_transcript: true
tags:
  - yc-library
  - video
  - series/paper-club
---

# Why Inference Matters 12x More Than Training

**Author:** [[Y Combinator]]  
**Series:** [[Paper Club]]  
**Video:** [Watch on YouTube](https://www.youtube.com/watch?v=mHNKuH-9OxU)  
**Length:** 1:50:48  
**Uploaded:** 2026-10-24  
**Source:** [YC Library](https://www.ycombinator.com/library/g5-why-inference-matters-12x-more-than-training)

## Summary

Paper Club: For every FLOP spent training a model, roughly six go to serving it each year. The hosts cover the full lifecycle of an inference request, why the gap between the best and worst provider serving the same open model is bigger than the gap between open and closed models, how a compiler built on search turns GPU hours into tokens, and how SGLang manages memory for the agent era.

## YouTube Description

This week’s Paper Club is all about inference. 

For every FLOP spent training a model, roughly six go to serving it each year — and getting that part right has produced over $220 billion in market cap in the last decade. But inference is much more than calling model.forward. Every token has to move through a complicated stack of routing, caching, scheduling, kernels, memory, and hardware, all while balancing speed, cost, and quality.

We brought together researchers and builders from Together AI, Ollama, Luminal, and SGLang & RadixArk to take us through that stack from end to end. We’ll see how a token gets from an API request to a GPU and back, why the same open model can perform differently depending on who serves it, and how new approaches to compilers and caching are making inference faster and dramatically more efficient.

Join us for the next Paper Club on November 4th, where we'll talk AI for biology: https://events.ycombinator.com/yc-paper-club-nov-4

Chapters:
00:00 - Why inference matters more than training
08:24 - Three kinds of inference innovation
12:14 - Dan Fu: the lifecycle of an inference request
42:18 - Jeff Morgan: not all open model tokens are the same
1:04:31 - Joe Fioti: compiling models with search, not heuristics
1:30:30 - Liangsheng Yin: SGLang and memory for the agent era

Apply to Y Combinator: https://www.ycombinator.com/apply
Work at a startup: https://www.ycombinator.com/jobs
