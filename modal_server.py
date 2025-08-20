import modal
import inspect

app = modal.App("ci-server")

def setup_runner():

    import requests
    import subprocess
    import uuid
    import os

    # Extract the GitHub Actions runner archive
    print("Extracting GitHub Actions runner archive...")
    subprocess.run(["tar", "xzf", "./actions-runner-linux-x64-2.323.0.tar.gz"])
    print("Extraction completed.")

    print("Making request to get registration token...")
    # Make a request to get the registration token
    github_access_token = os.environ["GITHUB_PERSONAL_ACCESS_TOKEN"]

    response = requests.post(
        "https://api.github.com/repos/advay-modal/ci-on-modal/actions/runners/registration-token",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {github_access_token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    )
    print(f"Response status code: {response.status_code}")
    token_data = response.json() 
    registration_token = token_data["token"]
    print(f"Registration token received: {registration_token[:5]}...")
    
    # Configure the runner with the registration token
    config_command = [
        "bash",
        "./config.sh",
        "--url", "https://github.com/advay-modal/ci-on-modal",
        "--token", registration_token,
        "--name", f"modal_runner_{uuid.uuid4().hex}",
        "--ephemeral", 
        "--unattended",
    ]
    
    print("Configuring GitHub Actions runner...")
    # Execute the configuration command
    subprocess.run(config_command)
    # List directory contents to verify files

    print("Starting GitHub Actions runner...")
    subprocess.run(["bash", "./run.sh"])   
    subprocess.run(["bash", "./run-helper.sh"])
    print("GitHub Actions runner process completed.")

setup_runner_text = inspect.getsource(setup_runner)
setup_runner_command = f"""{setup_runner_text}\n\nsetup_runner()"""    


sandbox_image = modal.Image.debian_slim(python_version="3.11").apt_install([
    "tar", "curl", "libc6", "libicu-dev", "libc-bin"
    ]).pip_install(["requests"]).env({
        "RUNNER_ALLOW_RUNASROOT": "1"
    }).run_commands([
        "curl -o actions-runner-linux-x64-2.323.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.323.0/actions-runner-linux-x64-2.323.0.tar.gz",
    ])


class_image = modal.Image.debian_slim().pip_install("fastapi[standard]")

with class_image.imports():
    from fastapi import Request

@app.cls(allow_concurrent_inputs=1000, image = class_image)
class ModalServer:

    def __init__(self):
        self.job_id_to_sandbox_id = {}

    @modal.fastapi_endpoint(method="POST")
    async def handle_web_request(self, request: Request):
        # Parse the request body to get the JSON data
        request_data = await request.json()
        
        if request_data["action"] == "queued":
            sb = modal.Sandbox.create(app=app, image = sandbox_image, secrets = [modal.Secret.from_name("github-secret")])
            p = sb.exec("python", "-c", setup_runner_command)
            self.job_id_to_sandbox_id[request_data["workflow_job"]["id"]] = sb.object_id
            # Read both stdout and stderr
            for line in p.stdout:
                # Avoid double newlines by using end="".
                print(line, end="")
            
            for line in p.stderr:
                # Print stderr with an indicator
                print(f"ERROR: {line}", end="")

        elif request_data["action"] == "completed":
            object_id = self.job_id_to_sandbox_id.get(request_data["workflow_job"]["id"], None)
            if object_id:
                sb = modal.Sandbox.from_id(object_id)
                sb.terminate()
                del self.job_id_to_sandbox_id[request_data["workflow_job"]["id"]]
