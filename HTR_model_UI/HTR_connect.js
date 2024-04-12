function analyze() {
    const fileInput = document.getElementById('imagefile');
    const file = fileInput.files[0];
    if (!file) {
        alert('Please select a file.');
        return;
    }

    const formData = new FormData();
    formData.append('file', file); // Append the file to FormData

    document.getElementById('configurator').classList.add("d-none");
    document.getElementById('configurator_load').classList.remove("d-none");

    fetch('http://127.0.0.1:3000/upload', {
        method: 'POST',
        body: formData
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(data.filepath);
            this.predict_text(data.filepath)
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}

function predict_text(filePath) {

    const requestData = {
        filePath: filePath
    };

    fetch('http://127.0.0.1:3000/runcmd', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(data);

            document.getElementById('configurator').classList.add("d-none");
            document.getElementById('configurator_load').classList.add("d-none");
            document.getElementById('configurator_result').classList.remove("d-none");

            document.getElementById('accuracy_r').innerHTML = ((data.accuracy) * 100) + "%";
            document.getElementById('name_r').innerHTML = data.name;
            document.getElementById('image_r').src = "http://localhost:3000/" + filePath;

            console.log('Response received:', data);
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });

}

