import AppRoutes from './routes'
import { AppProvider } from './contexts/AppContext'
import AppBar from './components/AppBar'

function App() {
  return (<div className="App">
    <AppProvider>
      <AppBar
        title="MiraVeja"
      />
      <AppRoutes />
    </AppProvider>
  </div>
  )
}

export default App
