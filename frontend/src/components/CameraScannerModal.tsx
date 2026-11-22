import { motion, AnimatePresence } from "motion/react";
import { useCallback, useEffect, useRef, useState } from "react";
import { useI18n } from "../i18n/I18nProvider";
import { Icon } from "./Icon";

const FLUTTER_APP_URL = "http://localhost:5174";

export function CameraScannerModal({
  isOpen,
  onClose,
  onCapture,
  documentKindLabel,
}: {
  isOpen: boolean;
  onClose: () => void;
  onCapture: (file: File) => void;
  documentKindLabel?: string;
}) {
  const { t } = useI18n();
  const [tab, setTab] = useState<"live" | "flutter">("live");
  const [facingMode, setFacingMode] = useState<"environment" | "user">("environment");
  const [capturedDataUrl, setCapturedDataUrl] = useState<string | null>(null);
  const [streaming, setStreaming] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // Whether the Flutter app is actually running, so the tab never claims a connection that isn't there.
  const [flutterUp, setFlutterUp] = useState<boolean | null>(null);

  useEffect(() => {
    if (!isOpen || tab !== "flutter") return;
    let cancelled = false;
    setFlutterUp(null);
    // An opaque no-cors response still means something answered; a refused connection rejects.
    fetch(FLUTTER_APP_URL, { mode: "no-cors", cache: "no-store" })
      .then(() => !cancelled && setFlutterUp(true))
      .catch(() => !cancelled && setFlutterUp(false));
    return () => {
      cancelled = true;
    };
  }, [isOpen, tab]);

  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const attemptRef = useRef(0); // bumped on every start/stop so a late-arriving stream can be detected

  const stopCamera = useCallback(() => {
    attemptRef.current++;
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setStreaming(false);
  }, []);

  const startCamera = useCallback(async () => {
    stopCamera();
    const attempt = ++attemptRef.current;
    setError(null);
    setLoading(true);

    try {
      let stream: MediaStream | null = null;
      try {
        // Try requested facing mode (ideal for mobile back camera)
        stream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: { ideal: facingMode },
            width: { ideal: 1920 },
            height: { ideal: 1080 },
          },
          audio: false,
        });
      } catch {
        // Fallback to any available video stream
        stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false,
        });
      }

      if (attempt !== attemptRef.current) {
        // The scanner was closed, flipped or restarted while the camera was starting (e.g. during
        // the permission prompt): turn this stream off, or the camera light stays on.
        stream.getTracks().forEach((track) => track.stop());
        return;
      }
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
        setStreaming(true);
      }
    } catch (err) {
      if (attempt !== attemptRef.current) return;
      console.warn("Live camera start failed:", err);
      setError(t("camera_permission_err"));
    } finally {
      if (attempt === attemptRef.current) setLoading(false);
    }
  }, [facingMode, stopCamera, t]);

  useEffect(() => {
    if (isOpen && tab === "live" && !capturedDataUrl) {
      startCamera();
    } else {
      stopCamera();
    }
    return () => {
      stopCamera();
    };
  }, [isOpen, tab, capturedDataUrl, startCamera, stopCamera]);

  function flipCamera() {
    setFacingMode((prev) => (prev === "environment" ? "user" : "environment"));
  }

  function handleCapture() {
    if (!videoRef.current) return;
    const video = videoRef.current;
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth || 1280;
    canvas.height = video.videoHeight || 720;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL("image/jpeg", 0.92);
    setCapturedDataUrl(dataUrl);
    stopCamera();
  }

  function handleUsePhoto() {
    if (!capturedDataUrl) return;
    fetch(capturedDataUrl)
      .then((res) => res.blob())
      .then((blob) => {
        const file = new File([blob], `scan_${Date.now()}.jpg`, { type: "image/jpeg" });
        onCapture(file);
        handleClose();
      });
  }

  function handleClose() {
    stopCamera();
    setCapturedDataUrl(null);
    onClose();
  }

  function handleMobileCameraFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) {
      onCapture(file);
      handleClose();
    }
  }

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/70 backdrop-blur-sm"
          onClick={handleClose}
        />

        {/* Modal Window */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 12 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 12 }}
          transition={{ duration: 0.2 }}
          className="relative z-10 w-full max-w-2xl overflow-hidden rounded-2xl border border-line bg-surface shadow-2xl"
          role="dialog"
          aria-modal="true"
        >
          {/* Header */}
          <div className="flex flex-wrap items-center justify-between border-b border-line px-5 py-3.5">
            <div className="flex items-center gap-2.5">
              <span className="grid h-9 w-9 place-items-center rounded-xl bg-[var(--accent-soft)] text-accent">
                <Icon name="camera" className="h-5 w-5" />
              </span>
              <div>
                <h3 className="font-semibold text-[16px] leading-tight">{t("camera_scanner_title")}</h3>
                {documentKindLabel && <span className="text-[12px] text-muted">{documentKindLabel}</span>}
              </div>
            </div>

            <div className="flex items-center gap-2">
              {/* Tab Selector */}
              <div className="seg text-xs" role="tablist">
                <button
                  type="button"
                  aria-selected={tab === "live"}
                  onClick={() => setTab("live")}
                  className={tab === "live" ? "font-semibold" : ""}
                >
                  {t("box_scan_title")}
                </button>
                <button
                  type="button"
                  aria-selected={tab === "flutter"}
                  onClick={() => setTab("flutter")}
                  className={tab === "flutter" ? "font-semibold" : ""}
                >
                  Dart / Flutter (:5174)
                </button>
              </div>

              <button
                type="button"
                className="btn text-muted hover:text-fg p-1.5"
                onClick={handleClose}
                aria-label="Close scanner"
              >
                <Icon name="close" className="h-5 w-5" />
              </button>
            </div>
          </div>

          {/* Modal Body */}
          <div className="p-4 sm:p-5">
            {tab === "flutter" ? (
              <div className="flex flex-col gap-3">
                <div className="flex items-center justify-between rounded-xl bg-accent/10 px-3.5 py-2.5 text-xs text-accent">
                  <span className="flex items-center gap-2">
                    <Icon name="shield" className="h-4 w-4" />
                    {flutterUp === null
                      ? "Dart / Flutter Evidence Screen (checking port 5174…)"
                      : flutterUp
                        ? "Dart / Flutter Evidence Screen (Connected on port 5174)"
                        : "Dart / Flutter app isn't running on port 5174"}
                  </span>
                  <a
                    href={FLUTTER_APP_URL}
                    target="_blank"
                    rel="noreferrer"
                    className="btn primary py-1 px-2.5 text-[11px]"
                  >
                    <Icon name="external" className="h-3 w-3" />
                    {t("flutter_open_app")}
                  </a>
                </div>
                {flutterUp === false ? (
                  <div className="grid h-[420px] w-full place-content-center gap-2 rounded-xl border border-line bg-surface-2 p-6 text-center text-[13px]">
                    <p className="m-0 font-semibold">Start the Flutter app to use this screen:</p>
                    <code className="rounded-lg bg-surface px-3 py-2 text-[12px]">
                      cd claim_sathi/claim_sathi_flutter &amp;&amp; flutter run -d chrome --web-port 5174
                    </code>
                    <p className="muted m-0">The live camera tab works without it.</p>
                  </div>
                ) : (
                  <div className="relative h-[420px] w-full overflow-hidden rounded-xl border border-line bg-black">
                    {flutterUp && (
                      <iframe
                        src={FLUTTER_APP_URL}
                        title="ClaimSaathi Flutter App Scanner"
                        className="h-full w-full border-0"
                        allow="camera; microphone; display-capture"
                      />
                    )}
                  </div>
                )}
              </div>
            ) : (
              <div className="flex flex-col items-center">
                {/* Viewfinder Container */}
                <div className="relative flex h-[340px] w-full items-center justify-center overflow-hidden rounded-xl bg-black sm:h-[380px]">
                  {capturedDataUrl ? (
                    <img
                      src={capturedDataUrl}
                      alt="Captured document preview"
                      className="h-full w-full object-contain"
                    />
                  ) : (
                    <>
                      <video
                        ref={videoRef}
                        playsInline
                        muted
                        autoPlay
                        className={`h-full w-full object-cover transition-opacity duration-300 ${
                          streaming ? "opacity-100" : "opacity-0"
                        }`}
                      />

                      {/* Align Document Guide Overlay */}
                      {streaming && (
                        <div className="pointer-events-none absolute inset-0 flex items-center justify-center p-6">
                          <div className="relative h-[85%] w-[90%] max-w-[420px] rounded-lg border-2 border-emerald-400/90 shadow-[0_0_0_9999px_rgba(0,0,0,0.35)]">
                            <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded bg-black/80 px-2.5 py-0.5 text-[11px] font-medium tracking-wide text-emerald-400">
                              {t("camera_align_doc")}
                            </span>
                            {/* Corner Accents */}
                            <div className="absolute top-0 left-0 h-4 w-4 border-t-4 border-l-4 border-emerald-400" />
                            <div className="absolute top-0 right-0 h-4 w-4 border-t-4 border-r-4 border-emerald-400" />
                            <div className="absolute bottom-0 left-0 h-4 w-4 border-b-4 border-l-4 border-emerald-400" />
                            <div className="absolute bottom-0 right-0 h-4 w-4 border-b-4 border-r-4 border-emerald-400" />
                          </div>
                        </div>
                      )}

                      {loading && (
                        <div className="absolute inset-0 flex flex-col items-center justify-center gap-2.5 text-white/80">
                          <div className="h-8 w-8 animate-spin rounded-full border-2 border-accent border-t-transparent" />
                          <span className="text-xs">{t("camera_starting")}</span>
                        </div>
                      )}

                      {error && (
                        <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center">
                          <Icon name="alert" className="mb-2 h-8 w-8 text-amber-400" />
                          <p className="max-w-[36ch] text-sm text-white/90">{error}</p>
                          <button
                            type="button"
                            className="btn primary mt-4 text-xs"
                            onClick={() => fileInputRef.current?.click()}
                          >
                            <Icon name="camera" />
                            {t("camera_device_photo")}
                          </button>
                        </div>
                      )}
                    </>
                  )}
                </div>

                {/* Hidden input for mobile camera capture fallback */}
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  capture="environment"
                  className="hidden"
                  onChange={handleMobileCameraFile}
                />

                {/* Bottom Controls */}
                <div className="mt-4 flex w-full flex-wrap items-center justify-between gap-2.5">
                  {capturedDataUrl ? (
                    <>
                      {/* Clearing the photo restarts the camera through the effect above; calling
                          startCamera() here as well opened two cameras and leaked one. */}
                      <button type="button" className="btn" onClick={() => setCapturedDataUrl(null)}>
                        <Icon name="refresh" />
                        {t("camera_retake")}
                      </button>
                      <button type="button" className="btn primary" onClick={handleUsePhoto}>
                        <Icon name="check" />
                        {t("camera_use_photo")}
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        type="button"
                        className="btn text-xs"
                        onClick={flipCamera}
                        disabled={!streaming}
                        title={t("camera_switch")}
                      >
                        <Icon name="refresh" className="h-4 w-4" />
                        <span className="hidden sm:inline">{t("camera_switch")}</span>
                      </button>

                      <button
                        type="button"
                        className="btn primary flex-1 max-w-[220px] py-2.5 text-sm font-semibold sm:flex-none"
                        onClick={handleCapture}
                        disabled={!streaming}
                      >
                        <Icon name="camera" className="h-4 w-4" />
                        {t("camera_capture")}
                      </button>

                      <button
                        type="button"
                        className="btn text-xs"
                        onClick={() => fileInputRef.current?.click()}
                        title={t("camera_device_photo")}
                      >
                        <Icon name="upload" className="h-4 w-4" />
                        <span className="hidden sm:inline">{t("camera_device")}</span>
                      </button>
                    </>
                  )}
                </div>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
