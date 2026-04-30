#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

/* ── Bubble Sort ── */
static void bubble_sort(int *a, int n) {
    for (int i = 0; i < n; i++) {
        int swapped = 0;
        for (int j = 0; j < n - 1 - i; j++) {
            if (a[j] > a[j+1]) {
                int t = a[j]; a[j] = a[j+1]; a[j+1] = t;
                swapped = 1;
            }
        }
        if (!swapped) break;
    }
}

/* ── Merge Sort ── */
static void merge(int *a, int *aux, int lo, int mid, int hi) {
    for (int k = lo; k <= hi; k++) aux[k] = a[k];
    int i = lo, j = mid + 1, k = lo;
    while (i <= mid && j <= hi)
        a[k++] = (aux[i] <= aux[j]) ? aux[i++] : aux[j++];
    while (i <= mid) a[k++] = aux[i++];
    while (j <= hi)  a[k++] = aux[j++];
}

static void merge_sort_r(int *a, int *aux, int lo, int hi) {
    if (lo >= hi) return;
    int mid = (lo + hi) / 2;
    merge_sort_r(a, aux, lo, mid);
    merge_sort_r(a, aux, mid+1, hi);
    merge(a, aux, lo, mid, hi);
}

static void merge_sort(int *a, int n) {
    int *aux = malloc(n * sizeof(int));
    merge_sort_r(a, aux, 0, n-1);
    free(aux);
}

/* ── Quick Sort ── */
static int partition(int *a, int lo, int hi) {
    int pivot = a[hi], i = lo;
    for (int j = lo; j < hi; j++)
        if (a[j] <= pivot) { int t = a[i]; a[i++] = a[j]; a[j] = t; }
    int t = a[i]; a[i] = a[hi]; a[hi] = t;
    return i;
}

static void quick_sort_r(int *a, int lo, int hi) {
    if (lo >= hi) return;
    int p = partition(a, lo, hi);
    quick_sort_r(a, lo, p-1);
    quick_sort_r(a, p+1, hi);
}

static void quick_sort(int *a, int n) {
    if (n > 1) quick_sort_r(a, 0, n-1);
}

/* ── Data generation ── */
static void gen(int *a, int n, const char *kind) {
    srand(42);
    for (int i = 0; i < n; i++) a[i] = rand() % (n * 10);
    if (strcmp(kind, "sorted") == 0) {
        /* simple insertion sort for generation */
        for (int i = 1; i < n; i++) {
            int key = a[i], j = i-1;
            while (j >= 0 && a[j] > key) { a[j+1] = a[j]; j--; }
            a[j+1] = key;
        }
    } else if (strcmp(kind, "reverse") == 0) {
        for (int i = 1; i < n; i++) {
            int key = a[i], j = i-1;
            while (j >= 0 && a[j] < key) { a[j+1] = a[j]; j--; }
            a[j+1] = key;
        }
    } else if (strcmp(kind, "mostly_sorted") == 0) {
        for (int i = 1; i < n; i++) {
            int key = a[i], j = i-1;
            while (j >= 0 && a[j] > key) { a[j+1] = a[j]; j--; }
            a[j+1] = key;
        }
        int swaps = n / 10;
        for (int s = 0; s < swaps; s++) {
            int i = rand() % (n-1);
            int t = a[i]; a[i] = a[i+1]; a[i+1] = t;
        }
    }
}

int main(int argc, char **argv) {
    if (argc != 4) { fprintf(stderr, "usage: sort_runner <algo> <n> <kind>\n"); return 1; }
    int n = atoi(argv[2]);
    int *a = malloc(n * sizeof(int));
    gen(a, n, argv[3]);
    if      (strcmp(argv[1], "bubble_sort") == 0) bubble_sort(a, n);
    else if (strcmp(argv[1], "merge_sort")  == 0) merge_sort(a, n);
    else if (strcmp(argv[1], "quick_sort")  == 0) quick_sort(a, n);
    else { fprintf(stderr, "unknown algo: %s\n", argv[1]); return 1; }
    free(a);
    return 0;
}
