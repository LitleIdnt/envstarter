from setuptools import setup, find_packages

setup(
    name="envstarter",
    version="1.0.0",
    description="Start your perfect work environment with one click",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "PyQt6>=6.6.0",
        "pystray>=0.19.4",
        "Pillow>=10.0.0",
        "winreg-path>=1.0.0",
        "psutil>=5.9.0",
    ],
    entry_points={
        "console_scripts": [
            "envstarter=envstarter.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "envstarter": ["resources/*"],
    },
)