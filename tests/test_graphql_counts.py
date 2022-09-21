from tests.fixtures import api

records_per_page = 1000


def get_count(api, project_name, connection_name):

    query = """
    query {{connection_name}}CountsTest(
        $projectName: String!,
        $first: Int = 1,
        $after: String,
    ){

        project(name: $projectName){
            {{connection_name}}(
                first: $first,
                after: $after
            ) {
                edges {
                    node { id }
                }

                pageInfo {
                    hasNextPage
                    endCursor
                }
            }
        }

    }

    """
    # cannot use fstrings. too much curly brackets :-/
    query = query.replace("{{connection_name}}", connection_name)
    count = 0
    cursor = None

    ids = []
    max_pages = 1000
    i = 0
    while i < max_pages:
        i += 1
        vars = {"projectName": project_name, "first": records_per_page}
        if cursor:
            vars["after"] = cursor

        response = api.gql(query, **vars)
        assert response
        connection = response["project"][connection_name]
        for edge in connection["edges"]:
            count += 1
            assert edge["node"]["id"] not in ids, f"Duplicity in {connection_name}"
            ids.append(edge["node"]["id"])

        if not connection["pageInfo"]["hasNextPage"]:
            break
        cursor = connection["pageInfo"]["endCursor"]

    return count


def process_project(api, project_name):
    response = api.get(f"/projects/{project_name}/stats")
    assert response

    expected_counts = response.data["counts"]

    for connection_name, expected_count in expected_counts.items():
        if expected_count > 20000:
            continue
        gql_count = get_count(api, project_name, connection_name)
        assert gql_count == expected_count


def test_entity_counts(api):
    response = api.get("projects")
    assert response
    project_names = [project["name"] for project in response.data["projects"]]
    for project_name in project_names:
        process_project(api, project_name)
