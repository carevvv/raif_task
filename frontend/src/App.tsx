import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Upload } from './pages/Upload'
import { ReceiptList } from './pages/ReceiptList'
import { ReceiptDetail } from './pages/ReceiptDetail'
import { Search } from './pages/Search'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/upload" replace />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/list" element={<ReceiptList />} />
          <Route path="/receipt/:id" element={<ReceiptDetail />} />
          <Route path="/search" element={<Search />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
