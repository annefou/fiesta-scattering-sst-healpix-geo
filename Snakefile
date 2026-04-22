"""
Snakefile for SST gap-filling experiment: Sphere vs WGS84 on HEALPix.

Usage:
    snakemake --cores 1
    snakemake --cores 1 -- ci   # CI mode (low resolution)
"""


rule all:
    input:
        "results/comparison_results.json",
        "results/comparison_rmse.png",


rule run_experiment:
    input:
        script="01_sphere_vs_wgs84.py",
    output:
        json="results/comparison_results.json",
        chart="results/comparison_rmse.png",
    params:
        ci_mode=os.environ.get("CI_MODE", "0"),
    shell:
        """
        export CI_MODE={params.ci_mode}
        jupytext --to notebook {input.script}
        jupyter execute 01_sphere_vs_wgs84.ipynb
        """


rule ci:
    input:
        "results/comparison_results.json",
        "results/comparison_rmse.png",
    shell:
        "echo 'CI run complete.'"
