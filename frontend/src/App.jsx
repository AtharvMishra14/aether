import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Play, X, Heart, Loader, Music, Send, ArrowLeft, MessageSquare } from 'lucide-react'
import './App.css'

// The Chameleon Variable: Uses Cloud URL if available, otherwise falls back to local testing
const API_URL = "https://aether-api-odgb.onrender.com";

function App() {
  const [token, setToken] = useState(null)
  const [profile, setProfile] = useState(null)
  const [matches, setMatches] = useState([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [loading, setLoading] = useState(false)
  const [chatMatch, setChatMatch] = useState(null) // Tracks if we are in an active chat

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const tokenFromUrl = urlParams.get('token')
    if (tokenFromUrl) {
      setToken(tokenFromUrl)
      window.history.replaceState({}, document.title, "/")
    }
  }, [])

  useEffect(() => {
    if (!token) return;
    const fetchData = async () => {
      setLoading(true)
      try {
        const profileRes = await fetch(`${API_URL}/profile`, {
          headers: { "Authorization": `Bearer ${token}` }
        });
        const profileData = await profileRes.json();
        setProfile(profileData);

        const matchesRes = await fetch(`${API_URL}/matches`, {
          headers: { "Authorization": `Bearer ${token}` }
        });
        const matchesData = await matchesRes.json();
        setMatches(matchesData.matches);
      } catch (error) {
        console.error("Failed to map data grid", error)
      }
      setLoading(false)
    }
    fetchData();
  }, [token])

  const handleLogin = () => {
    window.location.href = `${API_URL}/login`
  }

  const handleSwipe = async (action, targetId) => {
    const response = await fetch(`${API_URL}/connect`, {
      method: "POST",
      headers: { 
        "Authorization": `Bearer ${token}`, 
        "Content-Type": "application/json" 
      },
      body: JSON.stringify({ action, target_user_id: targetId })
    });
    
    const data = await response.json();
    
    // If the backend says it's a match, launch the Chat UI!
    if (data.mutual_match) {
      setChatMatch(matches[currentIndex]);
    } else {
      setCurrentIndex(prev => prev + 1);
    }
  }

  // --- UI STATE 1: Not Logged In ---
  if (!token) {
    return (
      <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
        <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} style={{ textAlign: 'center' }}>
          <h1 style={{ fontSize: '4rem', marginBottom: '10px' }}>Aether</h1>
          <p style={{ color: 'var(--text-muted)', marginBottom: '40px' }}>Discover your musical soulmate.</p>
          <motion.button 
            whileHover={{ scale: 1.05, backgroundColor: '#1ed760' }}
            whileTap={{ scale: 0.95 }}
            onClick={handleLogin}
            style={{ display: 'flex', alignItems: 'center', gap: '12px', background: 'var(--primary)', color: '#000', border: 'none', padding: '16px 32px', borderRadius: '50px', fontSize: '1.1rem', fontWeight: 'bold', cursor: 'pointer', margin: '0 auto' }}
          >
            <Play size={22} fill="#000" /> Connect with Spotify
          </motion.button>
        </motion.div>
      </div>
    )
  }

  // --- UI STATE 2: Loading Data ---
  if (loading || !profile || matches.length === 0) {
    return (
      <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '20px' }}>
        <Loader className="spinner" size={40} color="var(--primary)" />
        <p style={{ color: 'var(--text-muted)' }}>Synthesizing Musical DNA...</p>
      </div>
    )
  }

  // --- UI STATE 3: The Chat Room ---
  if (chatMatch) {
    return (
      <div style={{ display: 'flex', height: '100vh', flexDirection: 'column', background: 'var(--background)' }}>
        {/* Chat Header */}
        <div style={{ padding: '20px', background: 'var(--surface)', display: 'flex', alignItems: 'center', gap: '15px', borderBottom: '1px solid #334155' }}>
          <button 
            onClick={() => { setChatMatch(null); setCurrentIndex(prev => prev + 1); }}
            style={{ background: 'none', border: 'none', color: 'var(--text-main)', cursor: 'pointer', display: 'flex', alignItems: 'center' }}
          >
            <ArrowLeft size={24} />
          </button>
          <h2 style={{ margin: 0, fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <MessageSquare size={20} color="var(--primary)" /> 
            {chatMatch.name}
          </h2>
        </div>

        {/* Chat Body */}
        <div style={{ flex: 1, padding: '20px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '15px' }}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} style={{ alignSelf: 'center', background: 'rgba(29, 185, 84, 0.1)', color: 'var(--primary)', padding: '10px 20px', borderRadius: '20px', fontSize: '0.9rem', marginBottom: '10px' }}>
            It's a Vibe! You both love {chatMatch.shared_traits[0]}.
          </motion.div>
          
          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.5 }} style={{ background: 'var(--surface)', padding: '15px', borderRadius: '15px 15px 15px 0', maxWidth: '70%', alignSelf: 'flex-start' }}>
            Hey! I saw we both listen to {chatMatch.shared_traits.length > 1 ? chatMatch.shared_traits[1] : chatMatch.shared_traits[0]}. Got any playlist recommendations?
          </motion.div>
        </div>

        {/* Chat Input Box */}
        <div style={{ padding: '20px', background: 'var(--surface)', display: 'flex', gap: '10px' }}>
          <input 
            type="text" 
            placeholder="Type a message..." 
            style={{ flex: 1, background: '#334155', border: 'none', borderRadius: '25px', padding: '15px 20px', color: 'var(--text-main)', outline: 'none' }}
          />
          <button style={{ background: 'var(--primary)', border: 'none', borderRadius: '50%', width: '50px', height: '50px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
            <Send size={20} fill="#000" color="#000" />
          </button>
        </div>
      </div>
    )
  }

  const currentMatch = matches[currentIndex];

  // --- UI STATE 4: Empty Feed ---
  if (!currentMatch) {
    return (
      <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
        <h2 style={{ color: 'var(--text-muted)' }}>No more matches in your area.</h2>
      </div>
    )
  }

  // --- UI STATE 5: Active Match Feed ---
  return (
    <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', padding: '20px' }}>
      
      <div style={{ position: 'absolute', top: '20px', display: 'flex', alignItems: 'center', gap: '10px', background: 'var(--surface)', padding: '10px 20px', borderRadius: '30px' }}>
        <Music size={18} color="var(--primary)" />
        <span style={{ fontSize: '0.9rem', fontWeight: 'bold' }}>{profile.username} | {profile.genres[0]}</span>
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={currentMatch.user_id}
          initial={{ opacity: 0, x: 50, rotate: 5 }}
          animate={{ opacity: 1, x: 0, rotate: 0 }}
          exit={{ opacity: 0, x: -50, rotate: -5 }}
          transition={{ duration: 0.3 }}
          style={{ background: 'var(--surface)', padding: '40px', borderRadius: '20px', width: '100%', maxWidth: '400px', textAlign: 'center', boxShadow: '0 10px 30px rgba(0,0,0,0.5)' }}
        >
          <h2 style={{ fontSize: '2.5rem', marginBottom: '10px' }}>{currentMatch.name}</h2>
          
          <div style={{ display: 'inline-block', background: 'rgba(29, 185, 84, 0.2)', color: 'var(--primary)', padding: '8px 16px', borderRadius: '20px', fontWeight: 'bold', fontSize: '1.2rem', marginBottom: '20px' }}>
            {currentMatch.match_percentage}% Match
          </div>

          <p style={{ color: 'var(--text-muted)', marginBottom: '10px', fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '1px' }}>Shared Vibes</p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', justifyContent: 'center', marginBottom: '40px' }}>
            {currentMatch.shared_traits.length > 0 ? currentMatch.shared_traits.map(trait => (
              <span key={trait} style={{ background: '#334155', padding: '6px 12px', borderRadius: '8px', fontSize: '0.85rem' }}>
                {trait}
              </span>
            )) : <span style={{ color: 'var(--text-muted)' }}>Complete Opposites</span>}
          </div>

          <div style={{ display: 'flex', justifyContent: 'center', gap: '20px' }}>
            <motion.button 
              whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}
              onClick={() => handleSwipe('pass', currentMatch.user_id)}
              style={{ background: '#334155', border: 'none', width: '60px', height: '60px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}
            >
              <X size={28} color="#f8fafc" />
            </motion.button>
            <motion.button 
              whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}
              onClick={() => handleSwipe('like', currentMatch.user_id)}
              style={{ background: 'var(--primary)', border: 'none', width: '60px', height: '60px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', boxShadow: '0 4px 15px rgba(29, 185, 84, 0.4)' }}
            >
              <Heart size={28} color="#000" fill="#000" />
            </motion.button>
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  )
}

export default App