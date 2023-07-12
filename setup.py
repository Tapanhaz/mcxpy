from setuptools import setup

setup(
   name='mcxpy',
   version='0.0.3',
   description='For fetching mcx data',
   author='Tapan Hazarika',
   packages=['mcxpy'],
   package_data={'mcxpy': ['py.typed', '__init__.pyi', 'mcxpy.pyi']}
)

