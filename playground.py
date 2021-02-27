from flask import Flask, request
from c7n_mailer.utils import get_jinja_env
import jmespath
import json
import os

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def save_custodian_result():
    os.makedirs("data", exist_ok=True)
    custodian_result = request.data.decode("utf-8")

    result_json = json.loads(custodian_result)
    # Mail service adds an additional action key to the existing json holding notify mail action value
    action = jmespath.search("policy.actions[?type=='notify']| [?@.violation_desc] | [0]", custodian_result)
    result_json["action"] = action
    with open("data/custodian_result.json", "w") as f:
        f.write(json.dumps(result_json))
    return {"success": True}


@app.route("/template", methods=["GET"])
def template_test():
    # Load the template content
    template_name = request.args.get("name")
    if not template_name:
        template_name = "test_template.html.j2"

    env = get_jinja_env("templates")
    tm = env.get_template(template_name)

    # Read the payload json 
    with open("data/custodian_result.json", "r") as j:
        j_content = j.read()

    js = json.loads(j_content)
    # Consolidate and replace the variables used in template from loaded payload json 
    response_content = tm.render(js)

    # Return the final generated html template as response
    return response_content


if __name__ == '__main__':
    app.run(debug=True, port=5000)
