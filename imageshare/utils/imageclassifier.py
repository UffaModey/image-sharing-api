import tempfile
from gradio_client import Client, handle_file

client = Client("fafam/imageclassification")


def classify_image(image):
    # Save the PIL image to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".jpeg", delete=True) as temp_file:
        image.save(temp_file, format="JPEG")  # Save the image in an appropriate format
        temp_file.flush()  # Ensure all data is written to the file

        # Pass the temporary file's path to handle_file
        result = client.predict(
            img=handle_file(temp_file.name),
            api_name="/predict",
        )
    return result
