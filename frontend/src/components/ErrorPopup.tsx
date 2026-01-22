interface ErrorPopupProps {
  message: string;
  onClose: () => void;
}

function ErrorPopup({ message, onClose }: ErrorPopupProps) {
  return (
    <div className="error-overlay">
      <div className="error-popup">
        <div className="error-header">
          <h3>⚠️ Error</h3>
          <button className="error-close" onClick={onClose}>
            ✕
          </button>
        </div>
        <p className="error-message">{message}</p>
        <button className="error-btn" onClick={onClose}>
          Dismiss
        </button>
      </div>
    </div>
  );
}

export default ErrorPopup;
