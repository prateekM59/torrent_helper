from setuptools import setup

setup(name='torrent_helper',
      version='1.0',
      description='CLI tool for torrent download',
      long_description='A CLI/CMD tool that lets you search and download torrent without opening browser and bittorent client.',
      keywords='utorrent helper torrent helper CLI downloader windows',
      url='https://github.com/prateekM59/torrent_helper',
      author='Prateek Mahajan',
      author_email='prateekmahajan59@gmail.com',
      license='MIT',
      entry_points = {
          'console_scripts': [
               'get_torrent=torrent_helper.command_line:download_torrent'
          ],
      },
      packages = ['torrent_helper'],
      install_requires=[
      ],
      zip_safe=False) 