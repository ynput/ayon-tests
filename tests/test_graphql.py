from .fixtures import api, PROJECT_NAME


def test_graphql(api):

    return

    # create 100 folders in a loop
    for i in range(10):
        response = api.post(
            f"projects/{PROJECT_NAME}/folders",
            name=f"test_{i}",
            folderType="Asset",
        )
        assert response

        # for each folder create 100 subsets

        folder_id = response.data["id"]
        response = api.post(
            f"projects/{PROJECT_NAME}/subsets",
            folderId=folder_id,
            name=f"test_{i}",
            family="whatever",
        )

        assert response
        subset_id = response.data["id"]

        # for each subset create 100 versions

        for j in range(10):
            response = api.post(
                f"projects/{PROJECT_NAME}/versions",
                subsetId=subset_id,
                version=j,
            )

            assert response

        # for each folder create 100 tasks

        for k in range(10):
            response = api.post(
                f"projects/{PROJECT_NAME}/tasks",
                folderId=folder_id,
                name=f"taska_{i}_{k}",
                taskType="Generic",
            )
            assert response
