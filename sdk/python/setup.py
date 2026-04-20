from setuptools import setup, find_packages

setup(
    name="teder-sdk",
    version="0.1.0",
    description="SDK Python oficial do TEDER — API de segurança para agentes autônomos",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="MVR2 Soluções Tecnológicas Ltda",
    author_email="api@teder.com.br",
    url="https://github.com/ronyrechtman-wq/teder",
    packages=find_packages(),
    install_requires=["httpx>=0.27.0"],
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
