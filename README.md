# ARR for Data Professionals

## Preamble

<div class="alert alert-block alert-info">
Building ARR is simple, but that doesn't make it easy. The definitions seem to be where the problems take root. Depending on who you talk to or where you work, definitions can vary.<b> The important thing is consistency.</b> ARR is shiny and will get a lot of attention, so you better know what you're doing.</div>

## Introduction

The goal of this write up is to share my knowledge on building ARR datasets. I've built and scaled these datasets for companies less than $30M and more than $1B ARR. All the way from ingestion of source systems to desigining the visuals.

I'll explain how it all works, show some mistakes I've made, and make recommendations. Whether you are 12 sheets deep in excel or lost in spark configurations, as long as you are dealing with ARR on the data side, this is written for you. I'll start with what ARR is and how to calculate it. Then I'll dive into the customer cube. Build on top of our cube with all the different cuts and measures.

My goal is to generalize the code as much as possible. So, python with the usual data stack (pandas, numpy, etc.).

In terms of Finance and accounting, ARR is not to be confused with Revenue Recognition. ARR is Non-[GAAP](https://en.wikipedia.org/wiki/Accounting_standard). That distinction, I think, adds to a lot of chatter. [This article](https://sensiba.com/resources/insights/what-you-need-to-know-about-annual-recurring-revenue-and-gaap-revenue-recognition/) explains the difference well. Which means, everything I explain is not a law or notable standard. I'm just putting on paper everything I've been taught and been able to soak up from some pretty smart people.

## Table of Contents

- [What is ARR? Part 1](1-what-is-arr-part-1.ipynb)
- [What is ARR? Part 2](2-what-is-arr-part-2.ipynb)
- [What is ARR? Part 3](3-what-is-arr-part-3.ipynb)
- [The Customer Cube](4-the-customer-cube.ipynb)

