import os
import sys
import subprocess
import xml.etree.ElementTree as ET


def run_tests():

    project_dir = os.path.dirname(
        os.path.abspath(__file__)
    )

    xml_file = os.path.join(
        project_dir,
        "test-results.xml"
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            os.path.join(
                project_dir,
                "tests",
                "test_api.py"
            ),
            f"--junitxml={xml_file}",
            "-q"
        ],
        cwd=project_dir,
        capture_output=True,
        text=True
    )

    # If pytest did not generate the XML file
    if not os.path.exists(xml_file):

        error_message = (
            result.stdout
            + "\n"
            + result.stderr
        ).strip()

        return {
            "total_tests": 0,
            "passed": 0,
            "failed": 1,
            "pass_rate": 0,
            "tests": [
                {
                    "name": "Pytest execution",
                    "status": "ERROR",
                    "duration": "0",
                    "error": error_message
                }
            ]
        }

    tree = ET.parse(xml_file)
    root = tree.getroot()

    tests = []

    for testcase in root.iter("testcase"):

        test_name = testcase.attrib.get(
            "name",
            "Unknown test"
        )

        duration = testcase.attrib.get(
            "time",
            "0"
        )

        status = "PASSED"

        if testcase.find("failure") is not None:
            status = "FAILED"

        elif testcase.find("error") is not None:
            status = "ERROR"

        elif testcase.find("skipped") is not None:
            status = "SKIPPED"

        tests.append({
            "name": test_name,
            "status": status,
            "duration": duration
        })

    total_tests = len(tests)

    passed = sum(
        1 for test in tests
        if test["status"] == "PASSED"
    )

    failed = sum(
        1 for test in tests
        if test["status"] in ["FAILED", "ERROR"]
    )

    pass_rate = 0

    if total_tests > 0:
        pass_rate = round(
            (passed / total_tests) * 100,
            2
        )

    return {
        "total_tests": total_tests,
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
        "tests": tests
    }