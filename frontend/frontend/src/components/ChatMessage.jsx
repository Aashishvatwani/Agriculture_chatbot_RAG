import './ChatMessage.css';
import RichContent from './RichContent';
import { useEffect, useState } from 'react';
import { BotCartoonAvatar, UserCartoonAvatar } from './CartoonAvatar';

function ChatMessage({ message }) {
  const { type, content, richContent, timestamp, streaming, streamedChunks, sources, image } = message;
  const [streamedContent, setStreamedContent] = useState(content || '');
  const [parsedData, setParsedData] = useState({ answer: '', sections: [], citations: [] });
  
  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const formatText = (text) => {
    if (!text) return null;

    // Split by lines for processing
    const lines = text.split('\n');
    const elements = [];
    let currentList = [];
    let tableLines = [];
    let inTable = false;

    const processTable = (tableData) => {
      if (tableData.length === 0) return null;

      const rows = tableData.map(line => {
        return line.split('|')
          .map(cell => cell.trim())
          .filter(cell => cell.length > 0);
      });

      // Filter out separator rows (---)
      const dataRows = rows.filter(row => 
        !row.every(cell => /^[-:=\s]+$/.test(cell))
      );

      if (dataRows.length === 0) return null;

      // First row is header if it looks like one
      const hasHeader = dataRows.length > 1;
      const headerRow = hasHeader ? dataRows[0] : null;
      const bodyRows = hasHeader ? dataRows.slice(1) : dataRows;

      return (
        <div className="table-container">
          <table className="formatted-table">
            {headerRow && (
              <thead>
                <tr className="table-header-row">
                  {headerRow.map((cell, i) => (
                    <th key={i} className="table-header-cell">
                      {formatInlineMarkdown(cell)}
                    </th>
                  ))}
                </tr>
              </thead>
            )}
            <tbody>
              {bodyRows.map((row, rowIdx) => (
                <tr key={rowIdx} className="table-body-row">
                  {row.map((cell, cellIdx) => (
                    <td key={cellIdx} className="table-body-cell">
                      {formatInlineMarkdown(cell)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    };

    lines.forEach((line, idx) => {
      // Replace tabs with non-breaking spaces so indentation is preserved in HTML
      const original = line.replace(/\t/g, '\u00A0\u00A0\u00A0\u00A0');
      // Remove leading NBSPs for pattern matching but keep them for display
      const naked = original.replace(/^\u00A0+/, '');
      const trimmed = naked.trim();

      // Treat a whole-line wrapped in **...** as a header
      const fullBoldMatch = trimmed.match(/^\*\*(.+)\*\*$/);
      if (fullBoldMatch) {
        if (currentList.length > 0) {
          elements.push(<ul key={`list-${idx}`} className="formatted-list">{currentList}</ul>);
          currentList = [];
        }
        if (inTable && tableLines.length > 0) {
          const table = processTable(tableLines);
          if (table) elements.push(<div key={`table-${idx}`}>{table}</div>);
          tableLines = [];
          inTable = false;
        }
        elements.push(<h3 key={`bold-heading-${idx}`} className="formatted-header">{fullBoldMatch[1].trim()}</h3>);
        return;
      }

      // Treat a whole-line wrapped in *...* or _..._ as a subheader
      const fullItalicMatch = trimmed.match(/^[*_](.+)[*_]$/);
      if (fullItalicMatch && !trimmed.startsWith('* ') && !trimmed.startsWith('_ ')) {
        if (currentList.length > 0) {
          elements.push(<ul key={`list-${idx}`} className="formatted-list">{currentList}</ul>);
          currentList = [];
        }
        if (inTable && tableLines.length > 0) {
          const table = processTable(tableLines);
          if (table) elements.push(<div key={`table-${idx}`}>{table}</div>);
          tableLines = [];
          inTable = false;
        }
        elements.push(<h4 key={`italic-sub-${idx}`} className="formatted-subheader"><em>{fullItalicMatch[1].trim()}</em></h4>);
        return;
      }
      // Preserve explicit blank lines (either empty or tabs-only)
      if (original.trim().length === 0) {
        // render a visible blank line (keeps indentation if tabs were present)
        elements.push(<div key={`blank-${idx}`} className="blank-line">{original}</div>);
        return;
      }

      // Special source line styling
      if (trimmed.toLowerCase().startsWith('source:')) {
        if (currentList.length > 0) {
          elements.push(<ul key={`list-${idx}`} className="formatted-list">{currentList}</ul>);
          currentList = [];
        }
        if (inTable && tableLines.length > 0) {
          const table = processTable(tableLines);
          if (table) elements.push(<div key={`table-${idx}`}>{table}</div>);
          tableLines = [];
          inTable = false;
        }
        elements.push(<p key={`source-${idx}`} className="formatted-source">{trimmed}</p>);
        return;
      }

      // Headers (## or **bold text**)
      if (trimmed.startsWith('##')) {
        if (currentList.length > 0) {
          elements.push(<ul key={`list-${idx}`} className="formatted-list">{currentList}</ul>);
          currentList = [];
        }
        if (inTable && tableLines.length > 0) {
          const table = processTable(tableLines);
          if (table) elements.push(<div key={`table-${idx}`}>{table}</div>);
          tableLines = [];
          inTable = false;
        }
        const headerText = trimmed.replace(/^##\s*/, '').replace(/\*\*/g, '');
        elements.push(<h3 key={idx} className="formatted-header">{headerText}</h3>);
      }
      // Subheadings (###)
      else if (trimmed.startsWith('###')) {
        if (currentList.length > 0) {
          elements.push(<ul key={`list-${idx}`} className="formatted-list">{currentList}</ul>);
          currentList = [];
        }
        if (inTable && tableLines.length > 0) {
          const table = processTable(tableLines);
          if (table) elements.push(<div key={`table-${idx}`}>{table}</div>);
          tableLines = [];
          inTable = false;
        }
        const subheadText = trimmed.replace(/^###\s*/, '').replace(/\*\*/g, '');
        elements.push(<h4 key={idx} className="formatted-subheader">{subheadText}</h4>);
      }
      // Bullet points (- or * or •)
      else if (trimmed.match(/^[-*•]\s/)) {
        if (inTable && tableLines.length > 0) {
          const table = processTable(tableLines);
          if (table) elements.push(<div key={`table-${idx}`}>{table}</div>);
          tableLines = [];
          inTable = false;
        }
        const listText = trimmed.replace(/^[-*•]\s*/, '');
        const formatted = formatInlineMarkdown(original.replace(/^[-*•]\s*/, ''));
        currentList.push(<li key={`li-${idx}`}>{formatted}</li>);
      }
      // Table rows (|)
      else if (trimmed.includes('|') && trimmed.split('|').filter(c => c.trim()).length > 1) {
        if (currentList.length > 0) {
          elements.push(<ul key={`list-${idx}`} className="formatted-list">{currentList}</ul>);
          currentList = [];
        }
        inTable = true;
        // push trimmed table row for consistent splitting, but keep original for display when rendering cells
        tableLines.push(trimmed);
      }
      // Regular paragraph
      else if (trimmed.length > 0) {
        if (currentList.length > 0) {
          elements.push(<ul key={`list-${idx}`} className="formatted-list">{currentList}</ul>);
          currentList = [];
        }
        if (inTable && tableLines.length > 0) {
          const table = processTable(tableLines);
          if (table) elements.push(<div key={`table-${idx}`}>{table}</div>);
          tableLines = [];
          inTable = false;
        }
        // Use original to preserve leading tabs/indentation in rendered paragraph
        const formatted = formatInlineMarkdown(original);
        elements.push(<p key={idx} className="formatted-paragraph">{formatted}</p>);
      }
    });

    // Flush remaining list
    if (currentList.length > 0) {
      elements.push(<ul key="list-final" className="formatted-list">{currentList}</ul>);
    }
    // Flush remaining table
    if (inTable && tableLines.length > 0) {
      const table = processTable(tableLines);
      if (table) elements.push(<div key="table-final">{table}</div>);
    }

    return <div className="formatted-content">{elements}</div>;
  };

  // Parse text into structured sections and sources for a clear table view
  const parseStructured = (text) => {
    if (!text) return { sections: [], sources: [] };
    const lines = text.split('\n');
    const sources = [];
    const sections = [];

    // Collect source lines and mark them
    lines.forEach((ln) => {
      const t = ln.trim();
      const lower = t.toLowerCase();
      if (lower.startsWith('based on the provided data') && t.includes('files')) {
        // try to extract file paths
        const match = t.match(/files[\\/][^\s\.]+(?:_?[^\s\.]*)?\.csv/gi);
        if (match) {
          match.forEach(m => sources.push(m));
        }
      }
      if (lower.startsWith('files\\') || lower.startsWith('files/')) {
        const m = t.match(/files[\\/][^\s]+\.csv/gi);
        if (m) m.forEach(x => sources.push(x));
      }
      // also capture explicit CSV Row references
      if (/csv row/i.test(t) || /row \d+/i.test(t)) {
        sources.push(t);
      }
    });

    // Split into high-level sections using blank lines and colon-headers
    let currentTitle = 'Summary';
    let currentBody = [];
    const pushSection = () => {
      if (currentBody.length > 0) {
        sections.push({ title: currentTitle, body: currentBody.join('\n').trim() });
      }
    };

    lines.forEach((ln) => {
      const t = ln.trim();
      if (!t) {
        // blank -> section break
        pushSection();
        currentTitle = 'Details';
        currentBody = [];
        return;
      }
      // treat "Best" lines or lines ending with ':' as titles
      if (/^[A-Z].*:$/.test(t) || /^Best\b/i.test(t)) {
        // flush previous
        pushSection();
        currentTitle = t.replace(/:$/, '');
        currentBody = [];
      } else {
        currentBody.push(t);
      }
    });
    pushSection();

    // dedupe sources
    const uniqSources = Array.from(new Set(sources)).map(s => s.replace(/^\s+|\s+$/g, ''));
    return { sections, sources: uniqSources };
  };

  // Keep streamed content up-to-date when chunks arrive
  useEffect(() => {
    if (streaming) {
      if (Array.isArray(streamedChunks)) {
        setStreamedContent(streamedChunks.join(''));
      }
    } else {
      setStreamedContent(content || '');
    }
  }, [streaming, streamedChunks, content]);

  // Parse and structure content for better display
  useEffect(() => {
    if (!streamedContent && !streaming) return;
    
    const text = streamedContent || '';
    const lines = text.split('\n').filter(l => l.trim());
    
    // Extract main answer and structured parts
    let mainAnswer = [];
    const sections = [];
    const citations = [];
    let currentSection = null;
    
    lines.forEach((line) => {
      const trimmed = line.trim();
      const lower = trimmed.toLowerCase();
      
      // Detect source citations
      if (lower.startsWith('source:') || lower.includes('files/') || lower.includes('files\\')) {
        citations.push(trimmed);
        return;
      }
      
      // Detect section headers (lines ending with ':' or starting with keywords)
      if (/^(best|recommendation|answer|summary|details|note|instructions?):/i.test(trimmed)) {
        if (currentSection) {
          sections.push(currentSection);
        }
        currentSection = {
          title: trimmed.replace(/:$/, ''),
          content: []
        };
        return;
      }
      
      // Add to current section or main answer
      if (currentSection) {
        currentSection.content.push(trimmed);
      } else {
        mainAnswer.push(trimmed);
      }
    });
    
    // Flush last section
    if (currentSection) {
      sections.push(currentSection);
    }
    
    setParsedData({
      answer: mainAnswer.join('\n'),
      sections: sections,
      citations: citations
    });
  }, [streamedContent, streaming]);

  const formatInlineMarkdown = (text) => {
    // Handle bold (**text** or __text__) and italic (*text* or _text_)
    if (!text) return null;
    const nodes = [];
    const regex = /(\*\*(.+?)\*\*|__(.+?)__|\*(.+?)\*|_(.+?)_)/g;
    let lastIndex = 0;
    let match;
    let key = 0;
    while ((match = regex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        nodes.push(text.slice(lastIndex, match.index));
      }
      const bold = match[2] || match[3];
      const italic = match[4] || match[5];
      if (bold) {
        nodes.push(<strong key={`b-${key++}`}>{bold}</strong>);
      } else if (italic) {
        nodes.push(<em key={`i-${key++}`}>{italic}</em>);
      }
      lastIndex = regex.lastIndex;
    }
    if (lastIndex < text.length) {
      nodes.push(text.slice(lastIndex));
    }
    return nodes;
  };

  const renderStructuredContent = () => {
    return (
      <div className="structured-answer">
        {/* Main Answer Card */}
        {parsedData.answer && (
          <div className="answer-card">
            <div className="card-header">
              <span className="card-icon">💡</span>
              <h4>Answer</h4>
            </div>
            <div className="card-content">
              {parsedData.answer.split('\n').map((line, i) => (
                <p key={`ans-${i}`} className="answer-line">
                  {formatInlineMarkdown(line)}
                </p>
              ))}
            </div>
          </div>
        )}

        {/* Section Cards */}
        {parsedData.sections.map((section, idx) => (
          <div key={`sec-${idx}`} className="answer-card section-card">
            <div className="card-header">
              <span className="card-icon">📋</span>
              <h4>{section.title}</h4>
            </div>
            <div className="card-content">
              {section.content.map((line, i) => {
                // Check if line is a bullet point
                if (line.match(/^[-*•]\s/)) {
                  return (
                    <div key={`sec-${idx}-${i}`} className="bullet-item">
                      <span className="bullet">•</span>
                      <span>{formatInlineMarkdown(line.replace(/^[-*•]\s*/, ''))}</span>
                    </div>
                  );
                }
                return (
                  <p key={`sec-${idx}-${i}`} className="section-line">
                    {formatInlineMarkdown(line)}
                  </p>
                );
              })}
            </div>
          </div>
        ))}

        {/* Sources Card */}
        {(parsedData.citations.length > 0 || (sources && sources.length > 0)) && (
          <div className="answer-card sources-card">
            <div className="card-header">
              <span className="card-icon">📚</span>
              <h4>Sources</h4>
            </div>
            <div className="card-content">
              {parsedData.citations.map((cite, i) => (
                <div key={`cite-${i}`} className="source-item">
                  <span className="source-badge">CSV</span>
                  <span className="source-text">{cite.replace(/^source:\s*/i, '')}</span>
                </div>
              ))}
              {sources && sources.map((src, i) => (
                <div key={`src-${i}`} className="source-item">
                  <span className="source-badge">DB</span>
                  <span className="source-text">{src.source}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };


  return (
    <div className={`message-wrapper ${type}`}>
      {type === 'bot' && (
        <BotCartoonAvatar />
      )}
      
      <div className="message-content">
        <div className={`message-bubble ${type}`}>
          <div className="message-text">
            {type === 'bot' ? (
              streaming ? (
                <div className="streaming-wrapper">
                  <div className="streaming-text">{streamedContent}</div>
                  <span className="streaming-cursor" aria-hidden>▮</span>
                </div>
              ) : (
                renderStructuredContent()
              )
            ) : (
              <div>
                {image && (
                  <img 
                    src={image} 
                    alt="User upload" 
                    className="message-image" 
                    style={{ 
                      maxWidth: '100%', 
                      maxHeight: '200px', 
                      borderRadius: '8px', 
                      marginBottom: '8px', 
                      display: 'block' 
                    }} 
                  />
                )}
                <p>{content}</p>
              </div>
            )}
          </div>
          {richContent && <RichContent data={richContent} />}
        </div>
        <span className="message-time">{formatTime(timestamp)}</span>
      </div>

      {type === 'user' && (
        <UserCartoonAvatar />
      )}
    </div>
  );
}

export default ChatMessage;
