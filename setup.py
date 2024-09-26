from setuptools import setup, find_packages

setup(
    name="dictator_gen",
    version="0.1",
    packages=find_packages(),
    install_requires=[],  # Ajoute ici tes dépendances depuis requirements.txt si nécessaire
    author="Jérémie Lenoir",
    author_email="lenoir.jeremie@gmail.com",
    description="A Python library for dictatorship generation models",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/tonrepo/dictator_gen",  # Remplace par l'URL de ton dépôt
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
