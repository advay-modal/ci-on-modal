# Run Continuous Integration (CI) Tests on Modal using Self hosted runners

[This example repo](https://github.com/advay-modal/ci-on-modal)
is a demonstration of one pattern for running tests on Modal:
bring your existing package and test suite (here `my_pkg` and `test_lib`)
and run it using modal sandboxes as self hosted runners

To do this 

- Create a personal access token in github
- Set the personal access token in a modal [secret](https://modal.com/docs/guide/secrets#secrets) named `github-secret`
- `pip install modal`
- `modal deploy modal_server.py`

Then trigger CI runs and modal will handle all the compute scaling.
