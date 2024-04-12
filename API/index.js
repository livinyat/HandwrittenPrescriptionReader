const express = require('express');
const multer = require('multer');
const { spawn } = require('child_process');
const bodyParser = require('body-parser');
const path = require('path');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(bodyParser.json());
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, 'uploads');
    },
    filename: function (req, file, cb) {
        cb(null, Date.now() + path.extname(file.originalname));
    }
});

const upload = multer({ storage: storage });

app.post('/upload', upload.single('file'), (req, res) => {
    const filePath = req.file.path;
    res.json({ filepath: filePath });
});

app.post('/runcmd', (req, res) => {
    const { filePath } = req.body;
    if (!filePath) {
        return res.status(400).send('File path is required');
    }
    const pythonProcess = spawn('python', ['main_model.py', filePath]);
    let outputData = '';

    pythonProcess.stdout.on('data', (data) => {
        outputData = outputData + "##" + data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
    });

    pythonProcess.on('close', (code) => {
        var responseArray = outputData.split("##")
        var resultArray = (responseArray[3]).split("||");
        const responseObj = { "name": (resultArray[0]).trim(), "accuracy": ((resultArray[1].replace('\r', '')).replace('\n', '')).trim() };
        res.send(responseObj);
    });
});

app.listen(3000, () => {
    console.log('Server is running on port 3000');
});
