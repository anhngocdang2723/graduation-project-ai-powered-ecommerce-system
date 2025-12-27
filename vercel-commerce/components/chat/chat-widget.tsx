'use client';

import { useState, useRef, useEffect } from 'react';
import { ChatBubbleLeftRightIcon, XMarkIcon, PaperAirplaneIcon } from '@heroicons/react/24/outline';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  products?: any[];
}

interface QuickReply {
  label: string;
  value: string;
  metadata?: any;
}

// Helper component for Product Detail Card (Large display with full info)
const ProductDetailCard = ({ product, onBuy, onSimilar }: { product: any, onBuy: (variantTitle: string, productId: string, variantId: string) => void, onSimilar: (product: any) => void }) => {
  const [selectedVariantId, setSelectedVariantId] = useState<string>(
      product.variants && product.variants.length > 0 ? product.variants[0].id : ""
  );

  const selectedVariant = product.variants?.find((v: any) => v.id === selectedVariantId) || product.variants?.[0];

  // Debug logging
  useEffect(() => {
    console.log('[ProductDetailCard] Product data:', { 
      id: product.id, 
      title: product.title, 
      thumbnail: product.thumbnail,
      variants: product.variants,
      price: product.price
    });
  }, [product]);

  return (
      <div className="w-full rounded-lg border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-900 overflow-hidden mb-2">
          {/* Product Image */}
          <div className="relative w-full h-64 bg-neutral-200 dark:bg-neutral-800 overflow-hidden flex items-center justify-center">
              {product.thumbnail ? (
                  <Image
                      className="w-full h-full object-cover"
                      width={400}
                      height={400}
                      alt={product.title}
                      src={product.thumbnail}
                      onError={(e) => {
                        console.warn('[ProductDetailCard] Image load error:', product.thumbnail);
                      }}
                  />
              ) : (
                  <div className="text-center text-neutral-500 dark:text-neutral-400">
                      <div className="text-4xl mb-2">📦</div>
                      <p className="text-sm">Không có hình ảnh</p>
                  </div>
              )}
          </div>

          <div className="p-4">
              {/* Product Title */}
              <h3 className="text-lg font-bold text-black dark:text-white mb-2">
                  {product.title}
              </h3>

              {/* Price */}
              <div className="mb-3">
                  <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                      {selectedVariant 
                          ? `${selectedVariant.price?.toLocaleString('vi-VN')} ${selectedVariant.currency_code?.toUpperCase() || 'VND'}` 
                          : `${product.price?.toLocaleString('vi-VN')} ${product.currency_code?.toUpperCase() || 'VND'}`}
                  </p>
              </div>

              {/* Description */}
              {product.description && (
                  <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-4 line-clamp-3">
                      {product.description}
                  </p>
              )}

              {/* Variant Selector */}
              {product.variants && product.variants.length > 1 && (
                  <div className="mb-4">
                      <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                          Chọn loại:
                      </label>
                      <select 
                          value={selectedVariantId}
                          onChange={(e) => setSelectedVariantId(e.target.value)}
                          className="w-full p-2 text-sm rounded border border-neutral-300 dark:border-neutral-600 bg-neutral-50 dark:bg-neutral-800 text-black dark:text-white focus:outline-none focus:border-blue-500"
                      >
                          {product.variants.map((v: any) => (
                              <option key={v.id} value={v.id}>
                                  {v.title} - {v.price?.toLocaleString('vi-VN')} {v.currency_code?.toUpperCase() || 'VND'}
                              </option>
                          ))}
                      </select>
                  </div>
              )}

              {/* Stock Info */}
              {selectedVariant && (
                  <div className="mb-4 p-2 bg-neutral-100 dark:bg-neutral-800 rounded">
                      <p className="text-xs text-neutral-600 dark:text-neutral-400">
                          <span className="font-medium">Tồn kho:</span> {selectedVariant.inventory_quantity || 0} sản phẩm
                      </p>
                  </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-2">
                  <button
                      onClick={() => onSimilar(product)}
                      className="flex-1 rounded-lg border border-blue-600 py-2 text-sm font-bold text-blue-600 hover:bg-blue-50 transition-colors dark:hover:bg-neutral-800"
                  >
                      SP tương tự
                  </button>
                  <button
                      onClick={() => {
                          const variant = product.variants?.find((v: any) => v.id === selectedVariantId) || product.variants?.[0];
                          onBuy(variant ? variant.title : "", product.id, variant ? variant.id : "");
                      }}
                      className="flex-1 rounded-lg bg-blue-600 py-2 text-sm font-bold text-white hover:bg-blue-700 transition-colors"
                  >
                      Mua ngay
                  </button>
              </div>
          </div>
      </div>
  );
};

// Helper component for Product Card with Variant Selection (Compact)
const ProductCard = ({ product, onBuy, onSimilar }: { product: any, onBuy: (variantTitle: string, productId: string, variantId: string) => void, onSimilar: (product: any) => void }) => {
  const [selectedVariantId, setSelectedVariantId] = useState<string>(
      product.variants && product.variants.length > 0 ? product.variants[0].id : ""
  );

  const selectedVariant = product.variants?.find((v: any) => v.id === selectedVariantId) || product.variants?.[0];

  return (
      <div className="flex w-full flex-col border border-neutral-200 dark:border-neutral-700 rounded-lg bg-white dark:bg-neutral-900 overflow-hidden mb-2">
          <div className="relative flex w-full flex-row justify-between px-3 py-3">
              <Link href={`/product/${product.handle}`} className="flex flex-row space-x-4 w-full">
                  <div className="relative h-16 w-16 flex-shrink-0 cursor-pointer overflow-hidden rounded-md border border-neutral-300 bg-neutral-300 dark:border-neutral-700 dark:bg-neutral-900 dark:hover:bg-neutral-800">
                      {product.thumbnail && (
                          <Image
                              className="h-full w-full object-cover"
                              width={64}
                              height={64}
                              alt={product.title}
                              src={product.thumbnail}
                          />
                      )}
                  </div>

                  <div className="flex flex-1 flex-col text-base min-w-0">
                      <span className="leading-tight truncate font-medium text-black dark:text-white">
                          {product.title}
                      </span>
                      <p className="text-sm font-semibold text-neutral-900 dark:text-neutral-100 mt-1">
                          {selectedVariant 
                              ? `${selectedVariant.price} ${selectedVariant.currency_code?.toUpperCase() || 'VND'}` 
                              : `${product.price} ${product.currency_code?.toUpperCase() || 'VND'}`}
                      </p>
                  </div>
              </Link>
          </div>

          <div className="px-3 pb-3">
              {/* Variant Selector */}
              {product.variants && product.variants.length > 1 && (
                  <div className="mb-3">
                      <select 
                          value={selectedVariantId}
                          onChange={(e) => setSelectedVariantId(e.target.value)}
                          className="w-full text-xs p-2 rounded border border-neutral-200 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-800 text-black dark:text-white focus:outline-none focus:border-blue-500"
                      >
                          {product.variants.map((v: any) => (
                              <option key={v.id} value={v.id}>
                                  {v.title}
                              </option>
                          ))}
                      </select>
                  </div>
              )}

              <div className="flex gap-2">
                  <button
                      onClick={() => onSimilar(product)}
                      className="flex-1 rounded-full border border-blue-600 py-2 text-xs font-bold text-blue-600 hover:bg-blue-50 transition-colors flex items-center justify-center gap-1 dark:hover:bg-neutral-800"
                  >
                      <span>SP tương tự</span>
                  </button>
                  <button
                      onClick={() => {
                          const variant = product.variants?.find((v: any) => v.id === selectedVariantId) || product.variants?.[0];
                          onBuy(variant ? variant.title : "", product.id, variant ? variant.id : "");
                      }}
                      className="flex-1 rounded-full bg-blue-600 py-2 text-xs font-bold text-white hover:bg-blue-700 transition-colors flex items-center justify-center gap-1"
                  >
                      <span>Mua ngay</span>
                  </button>
              </div>
          </div>
      </div>
  );
};

export default function ChatWidget({ userType = 'guest', customerId, cartId: initialCartId }: { userType?: string, customerId?: string, cartId?: string }) {
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStaffMode, setIsStaffMode] = useState(false);
  const [currentCartId, setCurrentCartId] = useState(initialCartId);

  // Update cart ID if prop changes
  useEffect(() => {
    if (initialCartId) {
        setCurrentCartId(initialCartId);
    }
  }, [initialCartId]);
  
  // Initialize sessionId from localStorage or create new
  const [sessionId, setSessionId] = useState('');

  // Helper to save messages to local storage
  const saveMessagesToLocal = (sid: string, msgs: Message[]) => {
    if (!sid) return;
    localStorage.setItem(`chat_history_${sid}`, JSON.stringify(msgs));
  };

  // Helper to load messages from local storage
  const loadMessagesFromLocal = (sid: string): Message[] | null => {
    if (!sid) return null;
    const stored = localStorage.getItem(`chat_history_${sid}`);
    if (stored) {
      try {
        return JSON.parse(stored).map((m: any) => ({
            ...m,
            timestamp: new Date(m.timestamp)
        }));
      } catch (e) {
        console.error("Failed to parse local history", e);
        return null;
      }
    }
    return null;
  };

  useEffect(() => {
    const initSession = async () => {
        // If customer is logged in, try to get their active session from server
        if (customerId) {
            try {
                const res = await fetch(`http://localhost:8000/chat/session/active/${customerId}`);
                if (res.ok) {
                    const data = await res.json();
                    if (data.session_id) {
                        console.log('[ChatWidget] Resuming customer session:', data.session_id);
                        setSessionId(data.session_id);
                        localStorage.setItem('chat_session_id', data.session_id);
                        localStorage.setItem('chat_customer_id', customerId); // Link session to customer
                        return;
                    }
                }
            } catch (e) {
                console.error('[ChatWidget] Failed to fetch active session:', e);
            }
        }

        // Fallback to local storage or create new
        const stored = localStorage.getItem('chat_session_id');
        const storedCustomerId = localStorage.getItem('chat_customer_id');
        
        // If customer changed (login/logout), create new session
        if (storedCustomerId !== customerId) {
            console.log('[ChatWidget] Customer changed, creating new session');
            const newId = `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            localStorage.setItem('chat_session_id', newId);
            localStorage.setItem('chat_customer_id', customerId || '');
            setSessionId(newId);
            return;
        }
        
        // Resume existing session
        if (stored) {
            console.log('[ChatWidget] Resuming local session:', stored);
            setSessionId(stored);
        } else {
            // Create new session
            const newId = `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            console.log('[ChatWidget] Creating new session:', newId);
            localStorage.setItem('chat_session_id', newId);
            localStorage.setItem('chat_customer_id', customerId || '');
            setSessionId(newId);
        }
    };
    
    initSession();
  }, [customerId]); // Re-run if customerId changes (login/logout)

  const [suggestions, setSuggestions] = useState<QuickReply[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, suggestions]);

  // Fetch history and suggestions on load
  useEffect(() => {
    if (isOpen && sessionId) {
      // Load from localStorage ONLY if we haven't loaded from server yet
      // This prevents flickering and duplicate welcome messages
      if (messages.length === 0) {
        const localMsgs = loadMessagesFromLocal(sessionId);
        if (localMsgs && localMsgs.length > 0) {
          console.log('[ChatWidget] Quick load from localStorage:', localMsgs.length, 'messages');
          setMessages(localMsgs);
        }
      }

      // Then fetch from server to sync/update (this will override localStorage if different)
      fetchHistory(sessionId);
      
      // Fetch suggestions (root menu)
      fetchSuggestions();
    }
  }, [isOpen, sessionId]); // Add sessionId to dependency to ensure fetch runs when session is ready

  // When sessionId changes (e.g. new chat), we might want to reset messages if it wasn't handled by handleNewChat
  // But handleNewChat handles it.
  // The initial load handles the stored session.

  const fetchHistory = async (sid: string) => {
    try {
      const response = await fetch(`http://localhost:8000/chat/history/${sid}`);
      if (response.ok) {
        const data = await response.json();
        console.log('[ChatWidget] Loaded history from server:', data);
        
        if (data.messages && data.messages.length > 0) {
          // Server has history - this is the source of truth
          const history = data.messages.map((msg: any) => ({
            id: msg.id || `msg_${Date.now()}_${Math.random()}`,
            role: msg.role,
            content: msg.content,
            timestamp: new Date(msg.timestamp),
            products: msg.products || []
          }));
          setMessages(history);
          // Sync back to local storage for offline access
          saveMessagesToLocal(sid, history);
          console.log('[ChatWidget] Context restored:', history.length, 'messages');
        } else {
          // Server has no history - new session
          // Don't show welcome if user already has local cache (might be offline)
          const localMsgs = loadMessagesFromLocal(sid);
          if (localMsgs && localMsgs.length > 0) {
            console.log('[ChatWidget] Using local cache (offline mode)');
            setMessages(localMsgs);
          } else {
            // Truly new session - show welcome
            const welcomeMsg: Message = {
              id: 'welcome',
              role: 'assistant',
              content: 'Xin chào! Tôi là trợ lý AI của cửa hàng. Tôi có thể giúp bạn tìm sản phẩm, tra cứu đơn hàng hoặc trả lời các câu hỏi. Bạn cần hỗ trợ gì?',
              timestamp: new Date(),
            };
            setMessages([welcomeMsg]);
            saveMessagesToLocal(sid, [welcomeMsg]);
          }
        }
      }
    } catch (e) {
      console.error('[ChatWidget] Failed to fetch history from server:', e);
      // Network error - try to use local cache
      const localMsgs = loadMessagesFromLocal(sid);
      if (localMsgs && localMsgs.length > 0) {
        console.log('[ChatWidget] Using local cache due to network error');
        setMessages(localMsgs);
      } else {
        // Show welcome as fallback
        const welcomeMsg: Message = {
          id: 'welcome',
          role: 'assistant',
          content: 'Xin chào! Tôi là trợ lý AI của cửa hàng. (Offline mode)',
          timestamp: new Date(),
        };
        setMessages([welcomeMsg]);
      }
    }
  };

  const handleNewChat = () => {
    const newId = `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('chat_session_id', newId);
    setSessionId(newId);
    const welcomeMsg: Message = {
        id: 'welcome',
        role: 'assistant',
        content: 'Xin chào! Tôi là trợ lý AI của cửa hàng. Tôi có thể giúp bạn tìm sản phẩm, tra cứu đơn hàng hoặc trả lời các câu hỏi. Bạn cần hỗ trợ gì?',
        timestamp: new Date(),
    };
    setMessages([welcomeMsg]);
    saveMessagesToLocal(newId, [welcomeMsg]); // Save new session start
    fetchSuggestions(); // Reset to root suggestions
    console.log('[ChatWidget] Started new chat session:', newId);
  };

  const handleClearChat = async () => {
    if (!sessionId) return;
    
    try {
      // Clear on server
      const response = await fetch(`http://localhost:8000/chat/session/clear/${sessionId}`, {
        method: 'POST'
      });
      
      if (response.ok) {
        console.log('[ChatWidget] Cleared server history for:', sessionId);
      }
    } catch (e) {
      console.error('[ChatWidget] Failed to clear server history:', e);
    }
    
    // Clear localStorage
    localStorage.removeItem(`chat_history_${sessionId}`);
    
    // Reset UI
    const welcomeMsg: Message = {
      id: 'welcome',
      role: 'assistant',
      content: 'Lịch sử chat đã được xóa. Bạn cần hỗ trợ gì?',
      timestamp: new Date(),
    };
    setMessages([welcomeMsg]);
    saveMessagesToLocal(sessionId, [welcomeMsg]);
    fetchSuggestions();
    console.log('[ChatWidget] Cleared chat history');
  };

  // Re-fetch suggestions when userType changes (e.g. login/logout)
  useEffect(() => {
      if (isOpen) {
          fetchSuggestions();
      }
  }, [userType]);

  // Handle Add to Cart
  const handleAddToCart = async (productTitle: string, variantId: string) => {
    try {
      // Call API route to add to cart
      const response = await fetch('/api/cart/add-item', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          merchandiseId: variantId,
          quantity: 1,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to add to cart');
      }

      // Show success message
      const successMsg: Message = {
        id: `msg_${Date.now()}`,
        role: 'assistant',
        content: `✅ Đã thêm "${productTitle}" vào giỏ hàng!`,
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, successMsg]);
      saveMessagesToLocal(sessionId, [...messages, successMsg]);
      
      // Optional: Trigger cart refresh
      window.dispatchEvent(new Event('cartUpdated'));
      
    } catch (error) {
      console.error('[ChatWidget] Add to cart error:', error);
      
      const errorMsg: Message = {
        id: `msg_${Date.now()}`,
        role: 'assistant',
        content: '❌ Không thể thêm vào giỏ hàng. Vui lòng thử lại.',
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, errorMsg]);
      saveMessagesToLocal(sessionId, [...messages, errorMsg]);
    }
  };

  // Handle Similar Products
  const handleSimilarProducts = async (product: any) => {
    try {
      setIsLoading(true);
      
      // Call API to get similar products
      const response = await fetch(`/api/recommendations/similar?productId=${product.id}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch similar products');
      }

      const data = await response.json();
      
      if (data.recommendations && data.recommendations.length > 0) {
        // Create response message with similar products
        const similarMsg: Message = {
          id: `msg_${Date.now()}`,
          role: 'assistant',
          content: `🔍 Sản phẩm tương tự "${product.title}":`,
          timestamp: new Date(),
          products: data.recommendations
        };
        
        setMessages(prev => [...prev, similarMsg]);
        saveMessagesToLocal(sessionId, [...messages, similarMsg]);
      } else {
        // No similar products found
        const noResultMsg: Message = {
          id: `msg_${Date.now()}`,
          role: 'assistant',
          content: `😔 Không tìm thấy sản phẩm tương tự cho "${product.title}".`,
          timestamp: new Date(),
        };
        
        setMessages(prev => [...prev, noResultMsg]);
        saveMessagesToLocal(sessionId, [...messages, noResultMsg]);
      }
      
    } catch (error) {
      console.error('[ChatWidget] Similar products error:', error);
      
      const errorMsg: Message = {
        id: `msg_${Date.now()}`,
        role: 'assistant',
        content: '❌ Không thể tìm sản phẩm tương tự. Vui lòng thử lại.',
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, errorMsg]);
      saveMessagesToLocal(sessionId, [...messages, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchSuggestions = async (tag?: string) => {
    try {
      const response = await fetch('http://localhost:8000/chat/suggestions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_type: userType, tag })
      });
      if (response.ok) {
        const data = await response.json();
        // Map ContextNodeDTO to QuickReply format
        const mapped = data.suggestions.map((s: any) => ({
          label: s.label,
          value: s.tag || s.value || s.id, // Use tag if available, else value/id
          metadata: { type: s.type, value: s.value }
        }));
        
        // If we are navigating into a group (tag is present), add a "Back to Menu" option
        if (tag) {
            mapped.push({
                label: "⬅️ Quay lại",
                value: "", // Empty value to signal root/back
                metadata: { type: "group", isBack: true }
            });
        }

        setSuggestions(mapped);
      }
    } catch (e) {
      console.error("Failed to fetch suggestions", e);
    }
  };

  const handleSuggestionClick = (qr: QuickReply) => {
    // If it's a link, navigate
    if (qr.metadata?.type === 'link' && qr.metadata?.value) {
      // Use router for internal links to avoid full reload
      if (qr.metadata.value.startsWith('/')) {
        router.push(qr.metadata.value);
      } else {
        window.location.href = qr.metadata.value;
      }
      return;
    }

    // If it's a group (navigation), fetch children
    if (qr.metadata?.type === 'group') {
        // If it's the "Back" button (empty value), fetch root suggestions
        fetchSuggestions(qr.value || undefined);
        return;
    }

    // Otherwise send as message (Action)
    sendMessage(qr.label, qr.value);
  };

  const sendMessage = async (text: string = input, tag?: string) => {
    if (!text.trim() || isLoading) return;

    // Handle staff escalation
    if (tag === 'action:staff.escalate') {
      setIsLoading(true);
      try {
        const response = await fetch('http://localhost:8000/chat/escalate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ session_id: sessionId, reason: text })
        });
        
        if (response.ok) {
          const data = await response.json();
          setIsStaffMode(true);
          
          const escalationMessage: Message = {
            id: `msg_${Date.now()}_escalation`,
            role: 'assistant',
            content: data.message,
            timestamp: new Date(),
          };
          
          const updatedMessages = [...messages, escalationMessage];
          setMessages(updatedMessages);
          saveMessagesToLocal(sessionId, updatedMessages);
        }
      } catch (error) {
        console.error('Escalation error:', error);
      } finally {
        setIsLoading(false);
      }
      return;
    }

    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: text.trim(),
      timestamp: new Date(),
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    saveMessagesToLocal(sessionId, updatedMessages); // Save user message immediately

    setInput('');
    setSuggestions([]); // Clear suggestions while loading
    setIsLoading(true);

    try {
      // Use the current cart ID from props/state
      const cartId = currentCartId;
      console.log('[ChatWidget] Sending message with cartId:', cartId);

      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
          session_id: sessionId,
          tag: tag, // Pass the tag if available
          customer_id: customerId, // Pass customerId to link session
          metadata: { 
            user_type: userType,
            cart_id: cartId // Pass cartId to sync with backend
          }
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const assistantMessage: Message = {
          id: `msg_${Date.now()}_assistant`,
          role: 'assistant',
          content: data.response,
          timestamp: new Date(),
          products: data.products,
        };
        
        const finalMessages = [...updatedMessages, assistantMessage];
        setMessages(finalMessages);
        saveMessagesToLocal(sessionId, finalMessages); // Save assistant response
        
        // Update suggestions from response
        if (data.quick_replies) {
          setSuggestions(data.quick_replies);
        }

        // Handle actions (e.g. update cart)
        if (data.action) {
            if (data.action.type === 'api_call' && data.action.payload?.command === 'update_cart') {
                const newCartId = data.action.payload.cart_id;
                console.log('[ChatWidget] Updating cart ID:', newCartId);
                setCurrentCartId(newCartId);
                
                // Update cart cookie
                document.cookie = `cartId=${newCartId}; path=/; max-age=31536000; SameSite=Lax`;
                // Dispatch event for other components
                window.dispatchEvent(new Event('cart-updated'));
                // Refresh to ensure new cart is loaded
                router.refresh();
            }
        }
      } else {
        throw new Error('Failed to get response');
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMsg: Message = {
          id: `msg_${Date.now()}_error`,
          role: 'assistant',
          content: 'Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.',
          timestamp: new Date(),
      };
      const finalMessages = [...updatedMessages, errorMsg];
      setMessages(finalMessages);
      saveMessagesToLocal(sessionId, finalMessages);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      {/* Chat Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-blue-600 text-white shadow-lg transition-all hover:bg-blue-700 hover:scale-105"
        aria-label="Toggle chat"
      >
        {isOpen ? (
          <XMarkIcon className="h-6 w-6" />
        ) : (
          <ChatBubbleLeftRightIcon className="h-6 w-6" />
        )}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 z-50 flex h-[600px] w-[400px] flex-col rounded-lg border border-neutral-200 bg-white shadow-2xl dark:border-neutral-800 dark:bg-black">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-neutral-200 px-4 py-3 dark:border-neutral-800">
            <div className="flex items-center gap-2">
              <div className={`h-2 w-2 rounded-full ${isStaffMode ? 'bg-orange-500' : 'bg-green-500'}`}></div>
              <span className="font-medium text-black dark:text-white">
                {isStaffMode ? '🧑‍💼 Nhân viên hỗ trợ' : '🤖 Trợ lý AI'}
              </span>
            </div>
            <div className="flex items-center gap-2">
                <button
                    onClick={handleClearChat}
                    className="text-xs text-orange-600 hover:text-orange-700 border border-orange-300 px-2 py-1 rounded dark:text-orange-400 dark:hover:text-orange-300 dark:border-orange-700"
                    title="Xóa lịch sử chat"
                >
                    🗑️
                </button>
                <button
                    onClick={handleNewChat}
                    className="text-xs text-neutral-500 hover:text-black border border-neutral-200 px-2 py-1 rounded dark:text-neutral-400 dark:hover:text-white dark:border-neutral-700"
                    title="Tạo đoạn chat mới"
                >
                    Chat mới
                </button>
                <button
                onClick={() => setIsOpen(false)}
                className="text-neutral-500 hover:text-black dark:text-neutral-400 dark:hover:text-white"
                >
                <XMarkIcon className="h-5 w-5" />
                </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-lg px-4 py-2 ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-neutral-100 text-neutral-900 dark:bg-neutral-800 dark:text-neutral-100'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  
                  {/* Show products if available */}
                  {message.products && message.products.length > 0 && (
                    <div className="mt-3 space-y-3 w-full">
                      {message.products.slice(0, 1).map((product: any) => (
                        <ProductDetailCard 
                            key={product.id} 
                            product={product} 
                            onBuy={async (variantTitle, pid, vid) => {
                              await handleAddToCart(product.title + ' - ' + variantTitle, vid);
                            }} 
                            onSimilar={handleSimilarProducts}
                        />
                      ))}
                      {message.products.length > 1 && (
                        <div className="space-y-2">
                          {message.products.slice(1, 3).map((product: any) => (
                            <ProductCard 
                                key={product.id} 
                                product={product} 
                                onBuy={async (variantTitle, pid, vid) => {
                                  await handleAddToCart(product.title + ' - ' + variantTitle, vid);
                                }} 
                                onSimilar={handleSimilarProducts}
                            />
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-neutral-100 rounded-lg px-4 py-2 dark:bg-neutral-800">
                  <div className="flex space-x-1">
                    <div className="h-2 w-2 bg-neutral-500 rounded-full animate-bounce"></div>
                    <div className="h-2 w-2 bg-neutral-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="h-2 w-2 bg-neutral-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Suggestions / Quick Replies */}
          {suggestions.length > 0 && (
            <div className="px-4 py-2 flex flex-wrap gap-2 border-t border-neutral-200 bg-neutral-50/50 dark:border-neutral-800 dark:bg-neutral-900/50">
              {suggestions.map((qr, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSuggestionClick(qr)}
                  className="text-xs bg-neutral-100 hover:bg-neutral-200 text-neutral-800 px-3 py-1.5 rounded-full border border-neutral-200 transition-colors dark:bg-neutral-800 dark:hover:bg-neutral-700 dark:text-neutral-200 dark:border-neutral-700"
                >
                  {qr.label}
                </button>
              ))}
            </div>
          )}

          {/* Input */}
          <div className="border-t border-neutral-200 p-4 dark:border-neutral-800">
            <div className="flex flex-col gap-3">
              {/* Action Buttons Row */}
              <div className="flex items-center gap-2">
                {/* Image Upload Placeholder */}
                <button
                  onClick={() => alert('Chức năng gửi hình ảnh sẽ sớm được hỗ trợ!')}
                  className="flex items-center gap-1 rounded-lg border border-neutral-300 bg-white px-3 py-1.5 text-xs text-neutral-600 transition hover:bg-neutral-50 dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-400 dark:hover:bg-neutral-800"
                  title="Gửi hình ảnh"
                >
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <span className="hidden sm:inline">Hình ảnh</span>
                </button>

                {/* Voice Input Placeholder */}
                <button
                  onClick={() => alert('Chức năng nhập bằng giọng nói sẽ sớm được hỗ trợ!')}
                  className="flex items-center gap-1 rounded-lg border border-neutral-300 bg-white px-3 py-1.5 text-xs text-neutral-600 transition hover:bg-neutral-50 dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-400 dark:hover:bg-neutral-800"
                  title="Nhập bằng giọng nói"
                >
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                  </svg>
                  <span className="hidden sm:inline">Giọng nói</span>
                </button>

                {/* Call Staff Button */}
                <button
                  onClick={() => sendMessage('Tôi muốn được hỗ trợ bởi nhân viên', 'action:staff.escalate')}
                  className="flex-1 flex items-center justify-center gap-1 rounded-lg border border-orange-500 bg-orange-50 px-3 py-1.5 text-xs font-medium text-orange-700 transition hover:bg-orange-100 dark:border-orange-600 dark:bg-orange-950 dark:text-orange-400 dark:hover:bg-orange-900"
                  title="Gọi nhân viên hỗ trợ"
                >
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                  </svg>
                  <span>Gọi nhân viên</span>
                </button>
              </div>

              {/* Message Input Row */}
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Nhập tin nhắn..."
                  className="flex-1 rounded-lg border border-neutral-200 bg-white px-4 py-2 text-sm text-neutral-900 placeholder-neutral-400 focus:border-blue-500 focus:outline-none dark:border-neutral-700 dark:bg-neutral-900 dark:text-white dark:placeholder-neutral-500"
                  disabled={isLoading}
                />
                <button
                  onClick={() => sendMessage()}
                  disabled={isLoading || !input.trim()}
                  className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600 text-white transition hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <PaperAirplaneIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
