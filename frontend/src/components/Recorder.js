import { Button, Stack, Box, Typography, Alert } from "@mui/material";
import { useState, useRef } from "react";
import { useAuth } from "../hooks/useAuth";
import Webcam from "react-webcam";
import axios from "axios";
import api from "../services/api";
import { v4 as uuidv4 } from "uuid";

function Recorder() {
  const { user } = useAuth();
  const audioConstraints = {
    suppressLocalAudioPlayback: true,
    noiseSuppression: true,
    echoCancellation: true,
  };
  const videoConstraints = {
    facingMode: "user",
  };
  const [status, setStatus] = useState(0);
  const webcamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const [recordedChunks, setRecordedChunks] = useState([]);
  const maxTime = 1800; //30 minutos em segundos
  const intervalRef = useRef(0);
  const [timer, setTimer] = useState(["00", "00", "00"]);
  const [uploading, setUploading] = useState(false);

  const startRecord = () => {
    if (status === 0) {
      setStatus(1);

      let time = 0;

      // inicializa timer
      intervalRef.current = setInterval(() => {
        if (time < maxTime) {
          time++;

          let second = time % 60;
          let minute = Math.floor(time / 60) % 60;
          let hour = Math.floor(time / 3600) % 60;

          second = second < 10 ? "0" + second : second;
          minute = minute < 10 ? "0" + minute : minute;
          hour = hour < 10 ? "0" + hour : hour;

          setTimer([hour, minute, second]);
        } else {
          stopRecord();
        }
      }, 1000);

      // inicializa gravação
      mediaRecorderRef.current = new MediaRecorder(webcamRef.current.stream, {
        mimeType: "video/webm",
      });
      mediaRecorderRef.current.start();
      let localChunks = [];
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (typeof event.data === "undefined") return;
        if (event.data.size === 0) return;
        localChunks.push(event.data);
      };
      setRecordedChunks(localChunks);
    }
  };

  const stopRecord = () => {
    clearInterval(intervalRef.current);
    mediaRecorderRef.current.stop();
    setUploading(true);
    const record_id = uuidv4();

    // espera a gravação terminar
    mediaRecorderRef.current.onstop = (event) => {
      if (recordedChunks.length) {
        let filename = record_id + ".webm";
        let blob = new Blob(recordedChunks, {
          type: "video/webm",
        });

        let file = new File([blob], filename);

        // enviar gravação para o S3
        api
          .get("upload", {
            params: { filename: filename },
          })
          .then((response) => {
            // separar os campos da url assinada
            let formData = new FormData();
            Object.keys(response.data.fields).forEach((key) => {
              formData.append(key, response.data.fields[key]);
            });
            formData.append("file", file);

            axios.post(response.data.url, formData).then((response) => {
              // envia metadados da gravação para o DynamoDB
              api
                .post("record", {
                  record_id: record_id,
                  email: user["userEmail"],
                  duration: `${timer[0]}:${timer[1]}:${timer[2]}`,
                  video: filename,
                })
                .then((response) => {
                  setUploading(false);
                  setRecordedChunks([]);
                });
            });
          });
      }
    };

    setStatus(0);
    setTimer(["00", "00", "00"]);
  };

  return (
    <>
      <Stack alignItems="center" justifyContent="center">
        <Box>
          <Webcam
            audio={true}
            muted={true}
            videoConstraints={videoConstraints}
            audioConstraints={audioConstraints}
            ref={webcamRef}
          />
        </Box>
        <Box>
          <Typography variant="caption">
            * tempo máximo de gravação é de 30 minutos, após esse tempo a
            gravação será parada
          </Typography>
        </Box>
        <Box>
          <Typography variant="h4">
            {timer[0]}:{timer[1]}:{timer[2]}
          </Typography>
        </Box>
        <Box>
          <Button
            onClick={() => {
              startRecord();
            }}
            color="highlight"
          >
            Iniciar gravação
          </Button>
          <Button
            onClick={() => {
              stopRecord();
            }}
            color="highlight"
          >
            Parar gravação
          </Button>
        </Box>
        {uploading && (
          <Box>
            <Alert severity="info">
              O vídeo está sendo armazenado, continue na página!
            </Alert>
          </Box>
        )}
      </Stack>
    </>
  );
}

export default Recorder;
