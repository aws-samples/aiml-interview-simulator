import Recorder from "../components/Recorder";
import RecordsTable from "../components/RecordsTable";
import { Box, Container } from "@mui/material";

function Simulador() {
  return (
    <Container
      disableGutters
      maxWidth="md"
      component="main"
      sx={{ pt: 8, pb: 6 }}
    >      
    Se apresente e responda as três perguntas abaixo:
      <ul>
        <li>Cite um serviço de computação na AWS</li>
        <li>Como são cobrados os serviços AWS?</li>
        <li>Onde posso armazenar aquivos em objeto na AWS?</li>
      </ul>
      <Box display="flex" justifyContent="center" alignItems="center">
        <Recorder />
      </Box>
      <Box mt={2}>
        <RecordsTable />
      </Box>
    </Container>
  );
}

export default Simulador;
