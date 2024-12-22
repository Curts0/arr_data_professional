# ARR for Data Professionals

<div class="alert alert-block alert-info">
Building ARR is simple, but that doesn't make it easy. The definitions seem to be where the problems take root. Depending on who you talk to or where you work, definitions can vary.<b> The important thing is consistency.</b> ARR is shiny and will get a lot of attention, so you better know what you're doing.</div>

## Introduction

The goal of this write up is to share knowledge on building ARR datasets. I've built and scaled ARR datasets for companies with $30 million ARR to $1 billion ARR. All the way from source ingestion to visuals.

I'll explain how it all works, show the many mistakes I've made, and make recommendations. Whether you are 12 sheets deep in excel or lost in spark configurations, as long as you are dealing with ARR on the data side, this is written for you. I'll start with what ARR is and how to calculate it. Then I'll dive into the customer cube. Build on top of our cube with all the different cuts and measures.

My goal is to generalize the code as much as possible. So, python with the usual data stack (pandas, numpy, matplotlib, etc.).

ARR is a financial metric, but it's non-[GAAP](https://en.wikipedia.org/wiki/Accounting_standard). That distinction, I think, is cause for much of the confusion around ARR. Which means everything I explain is not a law or notable standard. I'm just putting on paper everything I've been taught and been able to soak up from some pretty smart people.

## Table of Contents

- [What is ARR? Part 1](1-what-is-arr-part-1.ipynb)
- [What is ARR? Part 2](2-what-is-arr-part-2.ipynb)
- [What is ARR? Part 3](3-what-is-arr-part-3.ipynb)
- [The Customer Cube](4-the-customer-cube.ipynb)
- [The Cuts](5-the-cuts.ipynb)
