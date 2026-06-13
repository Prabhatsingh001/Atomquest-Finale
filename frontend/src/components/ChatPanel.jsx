import React, { useEffect, useRef, useState } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { ChatMessage } from './ChatMessage';
import FileUploadButton from './FileUploadButton';
import { useChatStore } from '../stores/chatStore';

export function ChatPanel({ sessionId }) {
  const { messages, typingUsers, loadHistory, isLoading } = useChatStore();
  const { isConnected, sendMessage, sendTyping } = useWebSocket(sessionId);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (sessionId) {
      loadHistory(sessionId);
    }
  }, [sessionId, loadHistory]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, typingUsers]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim()) {
      sendMessage(inputValue.trim());
      setInputValue('');
      sendTyping(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleChange = (e) => {
    setInputValue(e.target.value);
    sendTyping(true);
  };

  const typingNames = Object.values(typingUsers).map(u => u.name);
  let typingText = '';
  if (typingNames.length === 1) typingText = `${typingNames[0]} is typing...`;
  else if (typingNames.length > 1) typingText = 'Multiple people are typing...';

  return (
    <div className="flex flex-col h-full bg-slate-900 text-slate-200">
      <div className="p-4 border-b border-slate-800 bg-slate-900 flex justify-between items-center z-10">
        <h3 className="font-semibold text-slate-100">Session Chat</h3>
        <span className="flex items-center text-xs text-slate-400">
          <span className={`w-2 h-2 rounded-full mr-2 ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></span>
          {isConnected ? 'Connected' : 'Disconnected'}
        </span>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
        {isLoading ? (
          <div className="flex justify-center items-center h-full text-slate-500 text-sm">
            Loading messages...
          </div>
        ) : messages.length === 0 ? (
          <div className="flex justify-center items-center h-full text-slate-500 text-sm text-center">
            No messages yet. <br/> Send a message to start the conversation!
          </div>
        ) : (
          messages.map(msg => <ChatMessage key={msg.id} message={msg} />)
        )}
        
        {typingText && (
          <div className="text-xs text-slate-400 italic mb-2 ml-1">
            {typingText}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-3 bg-slate-900 border-t border-slate-800">
        <form onSubmit={handleSubmit} className="relative flex items-end gap-2">
          <FileUploadButton 
            sessionId={sessionId} 
            onUploadError={(err) => alert(err)}
          />
          <textarea
            value={inputValue}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            className="flex-1 px-4 py-2 bg-slate-800 border border-slate-700 text-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-sm placeholder-slate-400"
            rows="1"
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || !isConnected}
            className="p-2 text-blue-500 hover:bg-slate-800 rounded-lg disabled:text-slate-600 disabled:hover:bg-transparent transition-colors mb-0.5"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
              <path d="M3.478 2.404a.75.75 0 0 0-.926.941l2.432 7.905H13.5a.75.75 0 0 1 0 1.5H4.984l-2.432 7.905a.75.75 0 0 0 .926.94 60.519 60.519 0 0 0 18.445-8.986.75.75 0 0 0 0-1.218A60.517 60.517 0 0 0 3.478 2.404Z" />
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
}
