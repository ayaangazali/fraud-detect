// Simple test to verify React is working

function TestApp() {
  return (
    <div style={{ padding: '50px', background: '#f0f0f0' }}>
      <h1 style={{ color: '#10b981' }}>✅ React is Working!</h1>
      <p>If you see this, React is rendering correctly.</p>
      <p>Current time: {new Date().toLocaleTimeString()}</p>
    </div>
  );
}

export default TestApp;
