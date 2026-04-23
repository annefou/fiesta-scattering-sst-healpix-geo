FROM mambaorg/micromamba:1.5-jammy

# git is required at build time to install the FOSCAT fork from git+https://
# (see environment.yml). The base micromamba image does not ship with git.
USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/*
USER $MAMBA_USER

COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml /tmp/environment.yml
RUN micromamba install -y -n base -f /tmp/environment.yml && \
    micromamba clean --all --yes

WORKDIR /app
COPY . /app

# Convert Jupytext to notebook and execute
CMD ["bash", "-c", "\
    eval \"$(micromamba shell hook --shell bash)\" && \
    micromamba activate base && \
    jupytext --to notebook 01_sphere_vs_wgs84.py && \
    jupyter execute 01_sphere_vs_wgs84.ipynb && \
    echo 'Done. Results in /app/results/'"]
