import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Box,
  Typography,
  Modal,
} from "@mui/material";
import { useCallback, useEffect, useState } from "react";
import { useAuth } from "../hooks/useAuth";
import VideoLibraryIcon from "@mui/icons-material/VideoLibrary";
import RefreshIcon from "@mui/icons-material/Refresh";
import api from "../services/api";
import { Assessment } from "@mui/icons-material";

const columns = [
  { id: "date", label: "Data", minWidth: 100 },
  { id: "duration", label: "Duração", minWidth: 100 },
  { id: "video", label: "Vídeo", minWidth: 100 },
  { id: "report", label: "Relatório", minWidth: 100 },
];

const modalStyle = {
  position: "absolute",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  width: "50%",
  bgcolor: "background.paper",
  boxShadow: 24,
  p: 4,
};

function RecordsTable() {
  const { user } = useAuth();
  const [records, setRecords] = useState([]);
  const [reportModal, setReportModal] = useState(false);
  const [metrics, setMetrics] = useState({
    transcription: "",
    feedback_bedrock: "",
    attention: "", // Adicionar nova propriedade
    objects: "", // Adicionar nova propriedade
  });

  const handleS3Link = (file) => {
    api
      .get("download", {
        params: { filename: file },
      })
      .then((response) => {
        window.open(response.data["url"]);
      });
  };

  // const handleOpenReport = (record) => {
  //   setMetrics(JSON.parse(record.report.replace(/'/g, '"')));
  //   setReportModal(true);
  // };
  const handleOpenReport = (record) => {
  const parsedReport = JSON.parse(record.report.replace(/'/g, '"'));
  
  // Handle objects safely
  let objects = [];
  try {
    if (record.objects && typeof record.objects === 'string') {
      const match = record.objects.trim().match(/\[.+\]/)?.[0];
      if (match) {
        objects = JSON.parse(match.replace(/'/g, '"'));
      }
    } else if (Array.isArray(record.objects)) {
      objects = record.objects;
    }
  } catch (error) {
    console.error('Error parsing objects:', error);
  }

  setMetrics({
    ...parsedReport,
    attention: record.attention,
    objects: objects,
  });
  setReportModal(true);
};
  const getAttentionString = (attentionValue) => {
    return attentionValue === "True" ? "Sim" : "Não";
  };
  const handleCloseReport = () => setReportModal(false);

  const refreshTable = useCallback((email) => {
    api
      .get("records", {
        params: { email: email },
      })
      .then((response) => {
        setRecords(response.data.results);
      })
      .catch((error) => {
        console.error("Error fetching records:", error);
        // Try to fetch directly with fetch API as a fallback
        fetch(`${api.defaults.baseURL}records?email=${encodeURIComponent(email)}`, {
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        })
        .then(response => response.text())
        .then(text => {
          try {
            // Try to parse the response as JSON
            const data = JSON.parse(text);
            setRecords(data.results || []);
          } catch (e) {
            console.error("Error parsing response:", e);
            // If the response contains Decimal values, try to clean it
            const cleanedText = text.replace(/\bDecimal\(['"]([\d.]+)['"]\)/g, '$1');
            try {
              const data = JSON.parse(cleanedText);
              setRecords(data.results || []);
            } catch (e2) {
              console.error("Failed to parse cleaned response:", e2);
              setRecords([]);
            }
          }
        })
        .catch(fetchError => {
          console.error("Fetch fallback failed:", fetchError);
          setRecords([]);
        });
      });
  }, []);

  useEffect(() => {
    refreshTable(user["userEmail"]);
  }, [refreshTable, user]);

  return (
    <Paper sx={{ width: "100%", overflow: "hidden" }}>
      <Box
        sx={{
          display: "flex",
          flexDirection: "row-reverse",
        }}
      >
        <Button
          onClick={() => {
            refreshTable(user["userEmail"]);
          }}
        >
          <RefreshIcon />
        </Button>
      </Box>
      <TableContainer sx={{ maxHeight: 440 }}>
        <Table stickyHeader aria-label="sticky table">
          <TableHead>
            <TableRow>
              {columns.map((column) => (
                <TableCell
                  key={column.id}
                  align={column.align}
                  style={{ minWidth: column.minWidth }}
                >
                  {column.label}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {records.map((row) => (
              <TableRow key={row.record_id}>
                {columns.map((column) => {
                  const value = row[column.id];
                  if (column.id === "video") {
                    return (
                      <TableCell key={column.id} align={column.align}>
                        {value !== "" ? (
                          <Button
                            onClick={() => {
                              handleS3Link(value);
                            }}
                          >
                            <VideoLibraryIcon />
                          </Button>
                        ) : (
                          <Typography>aguardando</Typography>
                        )}
                      </TableCell>
                    );
                  } else if (column.id === "report") {
                    return (
                      <TableCell key={column.id} align={column.align}>
                        {value !== "" ? (
                          <Button
                            onClick={() => {
                              handleOpenReport(row);
                            }}
                          >
                            <Assessment />
                          </Button>
                        ) : (
                          <Typography>aguardando</Typography>
                        )}
                      </TableCell>
                    );
                  } else {
                    return (
                      <TableCell key={column.id} align={column.align}>
                        <Typography>
                          {value !== "" ? value : "aguardando"}
                        </Typography>
                      </TableCell>
                    );
                  }
                })}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Modal
        open={reportModal}
        onClose={handleCloseReport}
        aria-labelledby="modal-modal-title"
        aria-describedby="modal-modal-description"
      >
        <Box sx={modalStyle}>
          <Typography id="modal-modal-title" variant="h4">
            Resultado da simulação
          </Typography>
          <Typography id="modal-modal-title" variant="h5" sx={{ mt: 2 }}>
            Feedback
          </Typography>
          <Typography id="modal-modal-description" sx={{ mt: 2 }}>
            {metrics.avaliacao}
          </Typography>
          <Typography id="modal-modal-title" variant="h5" sx={{ mt: 2 }}>
            Correção
          </Typography>
          <Typography id="modal-modal-description" sx={{ mt: 2 }}>
            {metrics.correcao}
          </Typography>
          <Typography id="modal-modal-title" variant="h5" sx={{ mt: 2 }}>
            Transcrição
          </Typography>
          <Typography id="modal-modal-description" sx={{ mt: 2 }}>
            {metrics.transcription}
          </Typography>
          <Typography id="modal-modal-title" variant="h5" sx={{ mt: 2 }}>
            Objetos [Óculos escudos e/ou Boné]
          </Typography>
           <Typography id="modal-modal-description" sx={{ mt: 2 }}>
            {metrics.objects.length > 0 ? (
              metrics.objects.map((obj, index) => (
                <span key={index}>
                  {obj}
                  {index !== metrics.objects.length - 1 ? ", " : ""}
                </span>
              ))
            ) : (
              "Nenhum objeto detectado"
            )}
          </Typography>
          <Typography id="modal-modal-title" variant="h5" sx={{ mt: 2 }}>
            Entrevistado estava Atento?
          </Typography>
          <Typography id="modal-modal-description" sx={{ mt: 2 }}>
            {getAttentionString(metrics.attention)}
          </Typography>
        </Box>
      </Modal>
    </Paper>
  );
}

export default RecordsTable;