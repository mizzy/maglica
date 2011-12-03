from setuptools import setup, find_packages
setup(
    name = "Maglica",
    version = "0.1",
    packages = find_packages(),
    scripts = [
      'scripts/maglica',
      'scripts/maglica_client_worker',
      'scripts/maglica_copy_worker',
      'scripts/maglica_host_worker',
      'scripts/maglica_zsh_completion',
    ],
    install_requires = [ 'PyYAML', 'termcolor' ],
    author = "Gosuke Miyashita",
    author_email = "gosukenator@gmail.com",
    description = "Simple internal cloud tool",
    url = "https://github.com/mizzy/maglica",
)
