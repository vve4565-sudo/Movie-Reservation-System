let accessTokenRefresh = null;

function saveAccessToken(response) {
  const authorization = response.headers.get("Authorization");
  if (!authorization) return;

  const token = authorization.replace(/^Bearer\s+/i, "").trim();
  if (token) {
    sessionStorage.setItem("cinemaAccessToken", token);
  }
}

async function refreshAccessToken(apiBase) {
  if (!accessTokenRefresh) {
    accessTokenRefresh = (async () => {
      const response = await fetch(`${apiBase}/auth/refresh`, {
        method: "GET",
        credentials: "include"
      });
      saveAccessToken(response);
      if (!response.ok) {
        throw new Error((await response.text()) || `HTTP ${response.status}`);
      }

      const token = sessionStorage.getItem("cinemaAccessToken");
      if (!token) {
        throw new Error("Ответ сервера не содержит новый access-токен.");
      }
      return token;
    })().finally(() => {
      accessTokenRefresh = null;
    });
  }
  return accessTokenRefresh;
}

async function isExpiredTokenResponse(response) {
  if (response.status !== 401 && response.status !== 403) return false;

  const body = await response.clone().text();
  let detail = body;
  try {
    detail = JSON.parse(body).detail ?? body;
  } catch {
    // Some API deployments return the error as plain text.
  }
  return String(detail).trim().toLowerCase() === "token expired";
}

async function cinemaApiFetch(apiBase, path, options = {}) {
  const sendRequest = () => {
    const headers = new Headers(options.headers);
    const token = sessionStorage.getItem("cinemaAccessToken");
    if (token) headers.set("Authorization", `Bearer ${token}`);

    return fetch(`${apiBase}${path}`, {
      ...options,
      headers,
      credentials: "include"
    });
  };

  let response = await sendRequest();
  saveAccessToken(response);

  if (path === "/auth/logout" && response.ok) {
    sessionStorage.removeItem("cinemaAccessToken");
    sessionStorage.removeItem("cinemaUser");
  }

  if (await isExpiredTokenResponse(response)) {
    try {
      await refreshAccessToken(apiBase);
    } catch (error) {
      throw new Error(`Не удалось обновить сессию: ${error.message}`);
    }
    response = await sendRequest();
    saveAccessToken(response);
  }

  return response;
}
