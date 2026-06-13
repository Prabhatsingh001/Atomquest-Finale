import React from 'react';
import { useAuthStore } from '../stores/authStore';

export function ChatMessage({ message }) {
  const { user } = useAuthStore();
  const isOwnMessage = user && message.sender_id === user.id;

  if (message.message_type === 'system') {
    return (
      <div className="flex justify-center my-2">
        <span className="text-xs text-slate-400 bg-slate-800 px-3 py-1 rounded-full border border-slate-700/50">
          {message.content}
        </span>
      </div>
    );
  }

  return (
    <div className={`flex flex-col mb-4 ${isOwnMessage ? 'items-end' : 'items-start'}`}>
      {!isOwnMessage && (
        <span className="text-xs text-slate-400 ml-1 mb-1 font-medium">
          {message.sender_name || 'User'}
        </span>
      )}
      <div 
        className={`px-4 py-2 rounded-2xl max-w-[90%] sm:max-w-[80%] ${
          isOwnMessage 
            ? 'bg-blue-600 text-white rounded-br-sm' 
            : 'bg-slate-800 border border-slate-700 text-slate-200 rounded-bl-sm shadow-sm'
        }`}
      >
        {message.message_type === 'file' ? (
          <div className="flex items-center gap-2 mt-1">
            <svg className="w-6 h-6 opacity-80" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
            </svg>
            <a 
              href={message.content.match(/\((.*?)\)/)?.[1] || '#'} 
              target="_blank" 
              rel="noopener noreferrer"
              className="underline underline-offset-2 hover:opacity-80 transition-opacity font-medium break-all"
            >
              {message.content.match(/\[(.*?)\]/)?.[1] || 'Attachment'}
            </a>
          </div>
        ) : (
          <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>
        )}
      </div>
      <span className="text-[10px] text-slate-500 mt-1 mx-1">
        {new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
      </span>
    </div>
  );
}
