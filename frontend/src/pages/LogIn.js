import {
  Stack,
  Box,
  Typography,
  TextField,
  Button,
  Alert,
} from "@mui/material";
import { useState } from "react";
import { useAuth } from "../hooks/useAuth";

function LogIn() {
  const { login } = useAuth();
  const [hasAlert, setHasAlert] = useState(false);
  const [severity, setSeverity] = useState("");
  const [message, setMessage] = useState("");

  const validateForm = (data) => {
    const emailRegex = /^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/;

    if (data.get("email").match(emailRegex)) {
      return true;
    } else {
      setHasAlert(true);
      setSeverity("error");
      setMessage("E-mail ou senha inválidos!");
      return false;
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault(); // não executa refresh no form submit
    const data = new FormData(event.currentTarget);
    if (validateForm(data)) {
      login({
        userEmail: data.get("email"),
        userPassword: data.get("password"),
      });
      setHasAlert(false);
    }
  };

  return (
    <Stack alignItems="center" justifyContent="center" sx={{ marginTop: 8 }}>
      <Typography component="h1" variant="h5">
        Fazer login
      </Typography>
      <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
        <TextField
          margin="normal"
          required
          fullWidth
          id="email"
          label="E-mail"
          name="email"
          autoComplete="email"
          autoFocus
        />
       {/*  <TextField
          margin="normal"
          required
          fullWidth
          name="password"
          label="Senha"
          type="password"
          id="password"
          autoComplete="current-password"
        />*/}
        <Button
          type="submit"
          fullWidth
          variant="contained"
          sx={{ mt: 3, mb: 2 }}
        >
          Fazer login
        </Button>
      </Box>
      {hasAlert && (
        <Box>
          <Alert severity={severity}>{message}</Alert>
        </Box>
      )}
    </Stack>
  );
}

export default LogIn;
