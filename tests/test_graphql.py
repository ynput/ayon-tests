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

        # for each folder create 100 products

        folder_id = response.data["id"]
        response = api.post(
            f"projects/{PROJECT_NAME}/products",
            folderId=folder_id,
            name=f"test_{i}",
            productType="whatever",
        )

        assert response
        product_id = response.data["id"]

        # for each product create 100 versions

        for j in range(10):
            response = api.post(
                f"projects/{PROJECT_NAME}/versions",
                productId=product_id,
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
