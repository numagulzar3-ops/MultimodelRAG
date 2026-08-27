
import { useRef, useState } from "react";
import "./App.css";

const API_URL = "https://multimodel-rag-api.onrender.com";

function App() {
  const fileInputRef = useRef(null);

  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const [uploading, setUploading] = useState(false);
  const [document, setDocument] = useState(null);

  // ==========================================================
  // UPLOAD DOCUMENT
  // ==========================================================

  const uploadDocument = async (event) => {
    const file = event.target.files[0];

    if (!file) return;

    const extension = file.name
      .substring(file.name.lastIndexOf("."))
      .toLowerCase();

    if (![".pdf", ".docx"].includes(extension)) {
      alert("Please upload a PDF or DOCX file.");
      event.target.value = "";
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setUploading(true);

    try {
      const response = await fetch(
        `${API_URL}/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Upload failed"
        );
      }

      setDocument({
        filename: data.filename,
        chunks: data.chunks,
      });

      setMessages([]);

    } catch (error) {
      console.error("Upload error:", error);

      alert(
        error.message ||
        "Something went wrong while uploading."
      );

    } finally {
      setUploading(false);
      event.target.value = "";
    }
  };


  // ==========================================================
  // ASK QUESTION
  // ==========================================================

  const askQuestion = async () => {
    if (!question.trim() || loading || !document) {
      return;
    }

    const userQuestion = question.trim();

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: userQuestion,
      },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/ask`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            question: userQuestion,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to get answer"
        );
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources || [],
        },
      ]);

    } catch (error) {
      console.error("Question error:", error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Sorry, I couldn't connect to the RAG backend.",
        },
      ]);

    } finally {
      setLoading(false);
    }
  };


  // ==========================================================
  // ENTER KEY
  // ==========================================================

  const handleKeyDown = (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      askQuestion();
    }
  };


  // ==========================================================
  // FILE SELECTOR
  // ==========================================================

  const openFileSelector = () => {
    fileInputRef.current?.click();
  };


  // ==========================================================
  // SOURCE CARD
  // ==========================================================

  const SourceCard = ({ source }) => {
    const [expanded, setExpanded] =
      useState(false);

    return (
      <div className="source-card">

        <button
          className="source-button"
          onClick={() =>
            setExpanded(!expanded)
          }
        >

          <div className="source-left">

            <div className="source-file-icon">
              📄
            </div>

            <div>

              <div className="source-name">
                {document?.filename || "Document"}
              </div>

              <div className="source-chunk">
                Chunk {source.chunk}
              </div>

            </div>

          </div>

          <div className="source-arrow">
            {expanded ? "⌃" : "⌄"}
          </div>

        </button>

        {expanded && (
          <div className="source-content">
            {source.text}
          </div>
        )}

      </div>
    );
  };


  // ==========================================================
  // UI
  // ==========================================================

  return (
    <div className="app">

      {/* ====================================================
          HEADER
      ==================================================== */}

      <header className="topbar">

        <div className="brand">

          <div className="brand-icon">
            ◈
          </div>

          <div>

            <div className="brand-name">
              MultiModel RAG
            </div>

            <div className="brand-subtitle">
              Local document intelligence
            </div>

          </div>

        </div>

        <div className="system-status">

          <span className="status-dot"></span>

          System Online

        </div>

      </header>


      {/* ====================================================
          APPLICATION
      ==================================================== */}

      <div className="workspace">

        {/* ==================================================
            SIDEBAR
        ================================================== */}

        <aside className="sidebar">

          <div className="sidebar-title">
            DOCUMENT
          </div>

          {document ? (

            <div className="document-card">

              <div className="document-card-icon">
                📄
              </div>

              <div className="document-card-info">

                <div className="document-name">
                  {document.filename}
                </div>

                <div className="document-meta">
                  {document.chunks} chunks
                </div>

              </div>

              <div className="document-check">
                ✓
              </div>

            </div>

          ) : (

            <div className="no-document">

              <div className="no-document-icon">
                📄
              </div>

              <div>
                No document uploaded
              </div>

            </div>

          )}

          <button
            className="upload-sidebar-button"
            onClick={openFileSelector}
            disabled={uploading}
          >

            <span>
              {uploading ? "⏳" : "+"}
            </span>

            {uploading
              ? "Processing..."
              : "Upload document"
            }

          </button>

          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx"
            onChange={uploadDocument}
            style={{ display: "none" }}
          />

          <div className="sidebar-info">

            <div className="info-title">
              Supported files
            </div>

            <div className="file-types">
              PDF &nbsp;•&nbsp; DOCX
            </div>

          </div>

        </aside>


        {/* ==================================================
            CHAT AREA
        ================================================== */}

        <main className="chat-area">

          <div className="chat-header">

            <div>

              <h1>
                Chat with your documents
              </h1>

              <p>
                Ask questions and get answers grounded
                in your uploaded document.
              </p>

            </div>

          </div>


          {/* =================================================
              MESSAGES
          ================================================= */}

          <div className="messages">

            {messages.length === 0 ? (

              <div className="welcome">

                <div className="welcome-icon">
                  ✦
                </div>

                <h2>
                  Your document, your questions.
                </h2>

                <p>
                  Upload a document to start
                  exploring its contents with AI.
                </p>

                <div className="suggestions">

                  <button
                    onClick={() =>
                      setQuestion(
                        "Summarize this document"
                      )
                    }
                    disabled={!document}
                  >
                    ✨ Summarize document
                  </button>

                  <button
                    onClick={() =>
                      setQuestion(
                        "What are the main concepts?"
                      )
                    }
                    disabled={!document}
                  >
                    💡 Main concepts
                  </button>

                  <button
                    onClick={() =>
                      setQuestion(
                        "Give me an example from the document"
                      )
                    }
                    disabled={!document}
                  >
                    📖 Give an example
                  </button>

                </div>

              </div>

            ) : (

              <div className="message-list">

                {messages.map(
                  (message, index) => (

                    <div
                      key={index}
                      className={`message-row ${message.role}`}
                    >

                      <div
                        className={`avatar ${message.role}`}
                      >

                        {message.role === "user"
                          ? "Y"
                          : "✦"}

                      </div>

                      <div className="message-body">

                        <div className="message-author">

                          {message.role === "user"
                            ? "You"
                            : "AI Assistant"}

                        </div>

                        <div className="message-text">
                          {message.content}
                        </div>

                        {message.role === "assistant" &&
                          message.sources &&
                          message.sources.length > 0 && (

                            <div className="sources">

                              <div className="sources-heading">
                                📚 Retrieved sources
                              </div>

                              {message.sources.map(
                                (source, sourceIndex) => (

                                  <SourceCard
                                    key={sourceIndex}
                                    source={source}
                                  />

                                )
                              )}

                            </div>

                          )}

                      </div>

                    </div>

                  )
                )}

                {loading && (

                  <div className="message-row assistant">

                    <div className="avatar assistant">
                      ✦
                    </div>

                    <div className="message-body">

                      <div className="message-author">
                        AI Assistant
                      </div>

                      <div className="typing">

                        <span></span>
                        <span></span>
                        <span></span>

                      </div>

                    </div>

                  </div>

                )}

              </div>

            )}

          </div>


          {/* =================================================
              INPUT
          ================================================= */}

          <div className="input-wrapper">

            <div className="input-box">

              <button
                className="paperclip"
                onClick={openFileSelector}
              >
                +
              </button>

              <input
                type="text"
                value={question}
                onChange={(event) =>
                  setQuestion(event.target.value)
                }
                onKeyDown={handleKeyDown}
                placeholder={
                  document
                    ? "Ask anything about your document..."
                    : "Upload a document to start chatting..."
                }
                disabled={
                  loading || !document
                }
              />

              <button
                className="send-button"
                onClick={askQuestion}
                disabled={
                  loading ||
                  !document ||
                  !question.trim()
                }
              >
                →
              </button>

            </div>

            <div className="input-hint">
              Press Enter to send
            </div>

          </div>

        </main>

      </div>

    </div>
  );
}

export default App;
