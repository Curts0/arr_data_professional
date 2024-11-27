# ARR for Data Profressionals

## Preamble

<div class="alert alert-block alert-info">
Building ARR is simple, but that doesn't make it easy. The definitions seem to be where the problems take root. Depending on who you talk to or where you work, definitions can vary.<b> The important thing is consistency.</b> ARR is shiny and will get a lot of attention, so you better know what you're doing.</div>

## Introduction

The goal of this write up is to share my knowledge on building ARR datasets. I've built and scaled these datasets for companies less than $\text{\$30M}$ and more than $\text{\$1B}$ ARR. All the way from ingestion of source systems to desigining the visuals.

I'll explain how it all works, show some mistakes I've made, and make recommendations. Whether you are 12 sheets deep in excel or lost in spark configurations, as long as you are dealing with ARR on the data side, this is written for you. I'll start with what ARR is and how to calculate it. Then I'll dive into the customer cube. Build on top of our cube with all the different cuts and measures.

My goal is to generalize the code as much as possible. So, python with the usual data stack (pandas, numpy, etc.).

In terms of Finance and accounting, ARR is not to be confused with Revenue Recognition. ARR is Non-[GAAP](https://en.wikipedia.org/wiki/Accounting_standard). That distinction, I think, adds to a lot of chatter. [This article](https://sensiba.com/resources/insights/what-you-need-to-know-about-annual-recurring-revenue-and-gaap-revenue-recognition/) explains the difference well. Which means, everything I explain is not a law or notable standard. I'm just putting on paper everything I've been taught and been able to soak up from some pretty smart people.

## Table of Contents

- [What is ARR? Part 1](2-what-is-arr-part-1.ipynb)
- [What is ARR? Part 2](3-what-is-arr-part-2.ipynb)
- [What is ARR? Part 3](4-what-is-arr-part-3.ipynb)
- [The Customer Cube](5-the-customer-cube.ipynb)

##### Packages used in Notebooks


```python
# Installing libraries used in entire notebook
# Written w/ Python3.12
%pip install pandas openpyxl matplotlib
```

    Defaulting to user installation because normal site-packages is not writeable
    Requirement already satisfied: pandas in c:\users\cstallings\appdata\local\packages\pythonsoftwarefoundation.python.3.12_qbz5n2kfra8p0\localcache\local-packages\python312\site-packages (2.2.3)
    Requirement already satisfied: openpyxl in c:\users\cstallings\appdata\local\packages\pythonsoftwarefoundation.python.3.12_qbz5n2kfra8p0\localcache\local-packages\python312\site-packages (3.1.5)
    Requirement already satisfied: matplotlib in c:\users\cstallings\appdata\local\packages\pythonsoftwarefoundation.python.3.12_qbz5n2kfra8p0\localcache\local-packages\python312\site-packages (3.9.2)
    Requirement already satisfied: numpy>=1.26.0 in c:\users\cstallings\appdata\local\packages\pythonsoftwarefoundation.python.3.12_qbz5n2kfra8p0\localcache\local-packages\python312\site-packages (from pandas) (2.1.1)
    Requirement already satisfied: python-dateutil>=2.8.2 in c:\users\cstallings\appdata\local\packages\pythonsoftwarefoundation.python.3.12_qbz5n2kfra8p0\localcache\local-packages\python312\site-packages (from pandas) (2.9.0.post0)
    Requirement already satisfied: pytz>=2020.1 in c:\users\cstallings\appdata\local\packages\pythonsoftwarefoundation.python.3.12_qbz5n2kfra8p0\localcache\local-packages\python312\site-packages (from pandas) (2024.2)
    Requirement already satisfied: tzdata>=2022.7 in c:\users\cstallings\appdata\local\packages\pythonsoftwarefoundation.python.3.12_qbz5n2kfra8p0\localcache\local-packages\python312\site-packages (from pandas) (2024.2)
    Requirement already satisfied: et-xmlfile in c:\users\cstallings\appdata\local\packages\pythonsoftwarefoundation.python.3.12_qbz5n2kfra8p0\localcache\local-packages\python312\site-packages (from openpyxl) (1.1.0)
    Requirement already satisfied: contourpy>=1.0.1 in c:\users\cstallings\appdata\local\packages\pythonsoftwarefoundation.python.3.12_qbz5n2kfra8p0\localcache\local-packages\python312\site-packages (from matplotlib) (1.3.0)
    Requirement already satisfied: cycler>=0.10 in c:\users\cstallings\appdata\local\packages\pythonsoftwarefoundation.python.3.12_qbz5n2kfra8p0\localcache\local-packages\python312\site-packages (from matplotlib) (0.12.1)
    Requirement already satisfied: fonttools>=4.22.0 in c:\users\cstallings\appdata\local\packages\pythonsoftwarefoundation.python.3.12_qbz5n2kfra8p0\localcache\local-packages\python312\site-packages (from matplotlib) (4.54.1)
    Requirement already satisfied: kiwisolver>=1.3.1 in c:\users\cstallings\appdata\local\packages\pythonsoftwarefoundation.python.3.12_qbz5n2kfra8p0\localcache\local-packages\python312\site-packages (from matplotlib) (1.4.7)
    Requirement already satisfied: packaging>=20.0 in c:\users\cstallings\appdata\local\packages\pythonsoftwarefoundation.python.3.12_qbz5n2kfra8p0\localcache\local-packages\python312\site-packages (from matplotlib) (24.1)
    Requirement already satisfied: pillow>=8 in c:\users\cstallings\appdata\local\packages\pythonsoftwarefoundation.python.3.12_qbz5n2kfra8p0\localcache\local-packages\python312\site-packages (from matplotlib) (10.4.0)
    Requirement already satisfied: pyparsing>=2.3.1 in c:\users\cstallings\appdata\local\packages\pythonsoftwarefoundation.python.3.12_qbz5n2kfra8p0\localcache\local-packages\python312\site-packages (from matplotlib) (3.1.4)
    Requirement already satisfied: six>=1.5 in c:\users\cstallings\appdata\local\packages\pythonsoftwarefoundation.python.3.12_qbz5n2kfra8p0\localcache\local-packages\python312\site-packages (from python-dateutil>=2.8.2->pandas) (1.16.0)
    Note: you may need to restart the kernel to use updated packages.
    

    
    [notice] A new release of pip is available: 24.2 -> 24.3.1
    [notice] To update, run: C:\Users\CStallings\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\python.exe -m pip install --upgrade pip
    
