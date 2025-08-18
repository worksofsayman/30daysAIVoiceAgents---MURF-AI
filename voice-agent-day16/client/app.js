(() => {
    const $ = (id) => document.getElementById(id);
  
    const wsUrlInput = $('wsUrl');
    const statusEl   = $('status');
    const connectBtn = $('connectBtn');
    const recordBtn  = $('recordBtn');
    const muteBtn    = $('muteBtn');
    const clearBtn   = $('clearBtn');
    const pingBtn    = $('testPingBtn');
    const bytesEl    = $('bytes');
    const timerEl    = $('timer');
    const codecEl    = $('codec');
    const pingEl     = $('ping');
    const waveCanvas = $('wave');
    const ctx        = waveCanvas.getContext('2d');
  
    // Resize canvas to device pixels
    function sizeCanvas() {
      const dpr = Math.max(1, window.devicePixelRatio || 1);
      waveCanvas.width  = Math.floor(waveCanvas.clientWidth  * dpr);
      waveCanvas.height = Math.floor(waveCanvas.clientHeight * dpr);
      ctx.scale(dpr, dpr);
    }
    sizeCanvas();
    window.addEventListener('resize', sizeCanvas);
  
    let ws = null;
    let mediaRecorder = null;
    let stream = null;
    let audioCtx = null;
    let analyser = null;
    let monitorNode = null;
    let animationId = null;
    let isRecording = false;
    let isMuted = true;
  
    let bytesSent = 0;
    let startTime = 0;
    let timerInterval = null;
  
    const supportedMime = (() => {
      const types = [
        'audio/webm;codecs=opus',
        'audio/webm',
        'audio/ogg;codecs=opus',
        'audio/ogg'
      ];
      for (const t of types) {
        if (window.MediaRecorder && MediaRecorder.isTypeSupported(t)) return t;
      }
      return ''; // Let browser decide
    })();
    codecEl.textContent = supportedMime || 'auto';
  
    function setStatus(text, color='var(--muted)') {
      statusEl.textContent = text;
      statusEl.style.color = color;
    }
  
    async function connectWS() {
      if (ws && ws.readyState === WebSocket.OPEN) return;
  
      setStatus('Connecting…', '#fde68a');
      ws = new WebSocket(wsUrlInput.value.trim());
      ws.binaryType = 'arraybuffer';
  
      ws.onopen = () => setStatus('Connected', '#86efac');
      ws.onclose = () => {
        setStatus('Disconnected', 'var(--muted)');
        if (isRecording) toggleRecord(); // auto-stop UI if socket died
      };
      ws.onerror = () => setStatus('WS Error', '#fca5a5');
      ws.onmessage = (ev) => {
        // simple PONG reader for ping test
        if (typeof ev.data === 'string' && ev.data === 'PONG') {
          const now = performance.now();
          const rtt = Math.round(now - lastPingTs);
          pingEl.textContent = `${rtt} ms`;
        }
      };
    }
  
    connectBtn.addEventListener('click', connectWS);
  
    async function setupAudio() {
      if (stream) return;
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const src = audioCtx.createMediaStreamSource(stream);
      analyser = audioCtx.createAnalyser();
      analyser.fftSize = 1024;
      src.connect(analyser);
  
      // optional monitor so user can hear themselves (muted by default)
      monitorNode = audioCtx.createGain();
      monitorNode.gain.value = isMuted ? 0 : 1;
      src.connect(monitorNode);
      monitorNode.connect(audioCtx.destination);
    }
  
    function drawWave() {
      const w = waveCanvas.clientWidth, h = waveCanvas.clientHeight;
      ctx.clearRect(0, 0, w, h);
  
      // base glow grid
      ctx.globalAlpha = 0.25;
      ctx.fillStyle = 'rgba(255,255,255,.03)';
      for (let x = 0; x < w; x += 24) ctx.fillRect(x, 0, 1, h);
      for (let y = 0; y < h; y += 16) ctx.fillRect(0, y, w, 1);
      ctx.globalAlpha = 1;
  
      const data = new Uint8Array(analyser.frequencyBinCount);
      analyser.getByteTimeDomainData(data);
  
      // waveform
      ctx.beginPath();
      const mid = h / 2;
      for (let i = 0; i < data.length; i++) {
        const x = (i / (data.length - 1)) * w;
        const y = mid + (data[i] - 128) / 128 * (h * 0.35);
        if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.lineWidth = 2;
      ctx.strokeStyle = '#00f5d4';
      ctx.shadowColor = '#00f5d4';
      ctx.shadowBlur = 10;
      ctx.stroke();
      ctx.shadowBlur = 0;
  
      animationId = requestAnimationFrame(drawWave);
    }
  
    function startTimer() {
      startTime = Date.now();
      timerInterval = setInterval(() => {
        const s = Math.floor((Date.now() - startTime) / 1000);
        const mm = String(Math.floor(s / 60)).padStart(2, '0');
        const ss = String(s % 60).padStart(2, '0');
        timerEl.textContent = `${mm}:${ss}`;
      }, 250);
    }
    function stopTimer() {
      clearInterval(timerInterval);
      timerEl.textContent = '00:00';
    }
  
    async function startRecording() {
      await connectWS();
      if (!ws || ws.readyState !== WebSocket.OPEN) {
        setStatus('Socket not open', '#fca5a5');
        return;
      }
      await setupAudio();
  
      // create MediaRecorder
      try {
        mediaRecorder = new MediaRecorder(stream, supportedMime ? { mimeType: supportedMime } : undefined);
      } catch (e) {
        console.error(e);
        setStatus('Recorder not supported', '#fca5a5');
        return;
      }
  
      bytesSent = 0;
      bytesEl.textContent = '0';
      isRecording = true;
      recordBtn.classList.add('active');
      startTimer();
      drawWave();
  
      mediaRecorder.ondataavailable = (evt) => {
        if (evt.data && evt.data.size > 0 && ws && ws.readyState === WebSocket.OPEN) {
          evt.data.arrayBuffer().then((buf) => {
            ws.send(buf);
            bytesSent += buf.byteLength;
            bytesEl.textContent = bytesSent.toLocaleString();
          });
        }
      };
      mediaRecorder.onerror = (e) => {
        console.error('MediaRecorder error', e);
        setStatus('Recorder error', '#fca5a5');
      };
  
      // Stream chunks every 400ms
      mediaRecorder.start(400);
      setStatus('Streaming', '#86efac');
    }
  
    function stopRecording() {
      if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
      }
      isRecording = false;
      recordBtn.classList.remove('active');
      cancelAnimationFrame(animationId);
      stopTimer();
      setStatus(ws && ws.readyState === WebSocket.OPEN ? 'Connected' : 'Disconnected',
                ws && ws.readyState === WebSocket.OPEN ? '#86efac' : 'var(--muted)');
    }
  
    async function toggleRecord() {
      if (!isRecording) startRecording();
      else stopRecording();
    }
  
    recordBtn.addEventListener('click', toggleRecord);
  
    muteBtn.addEventListener('click', () => {
      isMuted = !isMuted;
      if (monitorNode) monitorNode.gain.value = isMuted ? 0 : 1;
      muteBtn.textContent = isMuted ? '🔇 Mute Monitor' : '🔊 Unmute Monitor';
    });
  
    clearBtn.addEventListener('click', () => {
      bytesSent = 0;
      bytesEl.textContent = '0';
      pingEl.textContent = '—';
    });
  
    let lastPingTs = 0;
    pingBtn.addEventListener('click', () => {
      if (!ws || ws.readyState !== WebSocket.OPEN) return;
      lastPingTs = performance.now();
      ws.send('PING');
    });
  })();
  