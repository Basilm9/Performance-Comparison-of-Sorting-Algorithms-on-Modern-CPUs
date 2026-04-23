## ***Performance Comparison of Sorting Algorithms on Modern CPUs***

---

## **1\. Problem Description**

Sorting is a basic operation used in a lot of applications like databases and data processing. There are many different sorting algorithms, but they don’t all perform the same, especially as the size of the input increases.

The goal of this project is to compare the performance of three common sorting algorithms: Bubble Sort, Merge Sort, and Quick Sort. We want to see how their execution time changes as the input size grows and how their theoretical time complexities compare to actual performance on a modern CPU.

This is interesting because even though we learn time complexity like O(n), real performance can be affected by things like CPU efficiency, caching, and memory access patterns. So this project helps connect what we learn in theory to what actually happens when the code runs.

We expect Bubble Sort to perform much worse as the input size increases since it has O(n^2) complexity. Merge Sort and Quick Sort should perform better for larger inputs, with Quick Sort potentially being faster in practice due to better cache usage.

The main goal is to compare these algorithms using real data and understand how algorithm design and computer architecture both impact performance.

---

## **2\. Methodology**

To achieve the project goals, we will conduct an experimental evaluation of three sorting algorithms: Bubble Sort, Merge Sort, and Quick Sort.

First, each algorithm will be implemented in Python, ensuring that all implementations are consistent and comparable. Next, datasets of varying sizes will be generated using randomly distributed integer values. Example input sizes will include 1,000, 5,000, 10,000, 50,000, and 100,000 elements.

Performance will be measured using built-in timing tools such as the `time` module in Python. Each experiment will be executed multiple times, and the average runtime will be recorded to reduce variability in measurements.

All experiments will be conducted on the same machine under controlled conditions to ensure consistency. All algorithms will be tested under identical conditions to ensure fair benchmarking and accurate comparison of performance.

The collected data will be analyzed by plotting graphs that compare input size versus execution time for each algorithm. These results will then be compared against theoretical expectations to identify trends and differences.

Finally, we will interpret the results and discuss how CPU-related factors such as caching and memory access patterns may influence observed performance.

---

## **3\. Deliverables**

The project will include the following deliverables:

* **In-Class Presentation (6–7 minutes):**  
   A presentation summarizing the problem, methodology, experimental results, and key findings.

* **Final Written Report:**  
   A detailed report describing the methodology, experimental setup, results, and analysis, including graphs and comparisons to theoretical expectations.

* **Source Code:**  
   Well-documented implementations of all sorting algorithms, along with scripts used for testing and data collection.

---

## **4\. Team**

The project will be completed collaboratively, with each team member assigned specific responsibilities:

* **Basil Mohad – Algorithm Implementation Lead**  
   Responsible for implementing sorting algorithms and ensuring correctness and efficiency.

* **Andre Mercado – Data Collection & Testing Lead**  
   Responsible for running experiments, collecting timing data, and maintaining consistency across tests.

* **Zachery Terry – Data Analysis & Visualization Lead**  
   Responsible for generating graphs, analyzing trends, and assisting with the interpretation of results.

* **Ricky Mosqueda-Torres – Report & Presentation Lead**  
   Responsible for organizing the written report and preparing presentation materials.

All team members will contribute to the analysis, participate in the presentation, and review the final report.

