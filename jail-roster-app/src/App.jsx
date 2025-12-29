import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Checkbox } from '@/components/ui/checkbox.jsx'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Upload, Download, Plus, Edit, Trash2, Search, Filter, Users, Calendar, AlertCircle, FileUp, Loader2, LogOut, User, Settings, X, Image as ImageIcon, ZoomIn, FileText, Mail } from 'lucide-react'
import LoginForm from './components/LoginForm.jsx'
import './App.css'

function App() {
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [rosterData, setRosterData] = useState([])
  const [filteredData, setFilteredData] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [editingRecord, setEditingRecord] = useState(null)
  const [isImporting, setIsImporting] = useState(false)
  const [isExporting, setIsExporting] = useState(false)
  const [expandedRecordId, setExpandedRecordId] = useState(null)
  const [selectedPhotoRecord, setSelectedPhotoRecord] = useState(null)
  const [showEmailModal, setShowEmailModal] = useState(false)
  const [emailAddress, setEmailAddress] = useState('')
  const [isSendingEmail, setIsSendingEmail] = useState(false)
  const [activeTab, setActiveTab] = useState('active')

  const emptyRecord = {
    id: '',
    jailLocation: 'Solon',
    cell: '',
    dayNumber: '',
    totalNumber: '',
    name: '',
    dob: '',
    ssn: '',
    sexM: false,
    sexF: false,
    ocaNumber: '',
    arrestDateTime: '',
    misdemeanor: false,
    felony: false,
    charges: '',
    courtPacket: '',
    inst: '',
    courtCaseTicket: '',
    bondChangeNotice: false,
    bond: '',
    waiver: '',
    courtDate: '',
    releaseDateTime: '',
    holdersNotes: '',
    chargingDocs: '',
    suspectPhotoBase64: ''
  }

  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      const response = await fetch('/api/auth/me', { credentials: 'include' })
      if (response.ok) {
        const data = await response.json()
        setUser(data.user)
        await fetchRosterData()
      }
    } catch (error) {
      console.error('Auth check failed:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleLogin = (userData) => {
    setUser(userData)
    fetchRosterData()
  }

  const handleLogout = async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' })
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setUser(null)
      setRosterData([])
      setFilteredData([])
    }
  }

  const fetchRosterData = async () => {
    try {
      const response = await fetch('/api/roster', { credentials: 'include' })
      if (response.ok) {
        const data = await response.json()
        setRosterData(data)
        setFilteredData(data)
      } else if (response.status === 401) {
        setUser(null)
      }
    } catch (error) {
      console.error('Error fetching roster data:', error)
    }
  }

  // Separate active and released inmates
  const activeInmates = rosterData.filter(record => !record.releaseDateTime)
  const releasedInmates = rosterData.filter(record => record.releaseDateTime)

  useEffect(() => {
    const dataToFilter = activeTab === 'active' ? activeInmates : releasedInmates
    
    if (searchTerm === '') {
      setFilteredData(dataToFilter)
    } else {
      const filtered = dataToFilter.filter(record =>
        record.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        record.cell.toLowerCase().includes(searchTerm.toLowerCase()) ||
        record.ocaNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
        record.charges.toLowerCase().includes(searchTerm.toLowerCase())
      )
      setFilteredData(filtered)
    }
  }, [searchTerm, rosterData, activeTab])

  const handleAdd = () => {
    if (editingRecord && editingRecord.id.startsWith('new-')) {
      setEditingRecord(null)
    } else {
      setEditingRecord({ ...emptyRecord, id: `new-${Date.now()}` })
    }
  }

  const handleSave = async (updatedRecord) => {
    try {
      if (updatedRecord.id.startsWith('new-')) {
        const response = await fetch('/api/roster', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updatedRecord),
          credentials: 'include',
        })
        if (response.ok) await fetchRosterData()
        else if (response.status === 401) setUser(null)
      } else {
        const response = await fetch(`/api/roster/${updatedRecord.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updatedRecord),
          credentials: 'include',
        })
        if (response.ok) await fetchRosterData()
        else if (response.status === 401) setUser(null)
      }
    } catch (error) {
      console.error('Error saving record:', error)
    }
    setEditingRecord(null)
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this record?')) return
    try {
      const response = await fetch(`/api/roster/${id}`, { method: 'DELETE', credentials: 'include' })
      if (response.ok) await fetchRosterData()
      else if (response.status === 401) setUser(null)
    } catch (error) {
      console.error('Error deleting record:', error)
    }
  }

  const handleExportPDF = async () => {
    try {
      setIsExporting(true)
      const response = await fetch('/api/roster/export/pdf', { credentials: 'include' })
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `jail_roster_${new Date().toISOString().split('T')[0]}.pdf`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }
    } catch (error) {
      console.error('Error exporting PDF:', error)
      alert('Failed to export PDF')
    } finally {
      setIsExporting(false)
    }
  }

  const handleSendEmail = async () => {
    if (!emailAddress) {
      alert('Please enter an email address')
      return
    }

    try {
      setIsSendingEmail(true)
      const response = await fetch('/api/roster/export/pdf/email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: emailAddress }),
        credentials: 'include',
      })

      if (response.ok) {
        alert('Email sent successfully!')
        setShowEmailModal(false)
        setEmailAddress('')
      } else {
        const error = await response.json()
        alert(`Failed to send email: ${error.error}`)
      }
    } catch (error) {
      console.error('Error sending email:', error)
      alert('Failed to send email')
    } finally {
      setIsSendingEmail(false)
    }
  }

  const canDelete = () => user && user.role === 'admin'

  const getStatusBadge = (record) => {
    if (record.releaseDateTime) return <Badge variant="outline" className="bg-green-100">Released</Badge>
    if (record.courtDate) return <Badge variant="outline" className="bg-yellow-100">Pending Court</Badge>
    return <Badge variant="outline" className="bg-red-100">In Custody</Badge>
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    return date.toLocaleDateString()
  }

  if (isLoading) return <div className="flex items-center justify-center min-h-screen"><Loader2 className="h-8 w-8 animate-spin" /></div>
  if (!user) return <LoginForm onLogin={handleLogin} />

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Jail Roster Management System</h1>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">{user.username}</span>
            <Button variant="outline" size="sm" onClick={handleLogout}><LogOut className="h-4 w-4 mr-2" />Logout</Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search and Action Buttons */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
          <div className="flex-1 w-full">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search by name, cell, OCA #, or charges..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          <div className="flex gap-2">
            <Button onClick={handleExportPDF} size="sm" variant="outline" disabled={isExporting}>
              {isExporting ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <FileText className="h-4 w-4 mr-2" />}
              Export PDF
            </Button>
            <Button onClick={() => window.print()} size="sm" variant="outline">
              <FileText className="h-4 w-4 mr-2" />
              Print
            </Button>
            <Button onClick={() => setShowEmailModal(true)} size="sm" variant="outline">
              <Mail className="h-4 w-4 mr-2" />
              Email Report
            </Button>
            <Button onClick={handleAdd} size="sm" variant={editingRecord && editingRecord.id.startsWith('new-') ? 'destructive' : 'default'}>
              {editingRecord && editingRecord.id.startsWith('new-') ? (
                <><X className="h-4 w-4 mr-2" />Cancel Add</>
              ) : (
                <><Plus className="h-4 w-4 mr-2" />Add Record</>
              )}
            </Button>
          </div>
        </div>

        {/* Inline Add/Edit Form */}
        {editingRecord && (
          <Card className={`mb-6 border-2 ${editingRecord.id.startsWith('new-') ? 'border-blue-500' : 'border-yellow-500'}`}>
            <CardHeader>
              <CardTitle className={`text-xl ${editingRecord.id.startsWith('new-') ? 'text-blue-600' : 'text-yellow-600'}`}>
                {editingRecord.id.startsWith('new-') ? 'Add New Inmate Record' : `Edit Inmate Record: ${editingRecord.name}`}
              </CardTitle>
              <CardDescription>
                {editingRecord.id.startsWith('new-') ? 'Enter the details for the new inmate record below.' : 'Update the inmate record information below.'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <EditRecordForm
                record={editingRecord}
                onSave={handleSave}
                onCancel={() => setEditingRecord(null)}
                isAddMode={editingRecord.id.startsWith('new-')}
              />
            </CardContent>
          </Card>
        )}

        {/* Inmate Records Table with Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full max-w-md grid-cols-2 mb-6">
            <TabsTrigger value="active">
              Active Inmates ({activeInmates.length})
            </TabsTrigger>
            <TabsTrigger value="released">
              Released / History ({releasedInmates.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="active">
            <Card>
              <CardHeader>
                <CardTitle>Active Inmates ({filteredData.length})</CardTitle>
                <CardDescription>
                  Current inmates in custody
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto print-area">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-[8%]">Photo</TableHead>
                        <TableHead className="w-[8%]">Location</TableHead>
                        <TableHead className="w-[5%]">Cell</TableHead>
                        <TableHead className="w-[15%]">Name</TableHead>
                        <TableHead className="w-[10%]">OCA #</TableHead>
                        <TableHead className="w-[10%]">Arrest Date</TableHead>
                        <TableHead className="w-[25%]">Charges</TableHead>
                        <TableHead className="w-[10%]">Status</TableHead>
                        <TableHead className="w-[9%]">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>

                  {filteredData.map((record) => (
                    <React.Fragment key={record.id}>
                      <TableRow className="bg-white hover:bg-gray-50">
                        <TableCell>
                          {record.suspectPhotoBase64 ? (
                            <button
                              onClick={() => setSelectedPhotoRecord(record)}
                              className="relative group"
                            >
                              <img
                                src={record.suspectPhotoBase64}
                                alt={record.name}
                                className="h-10 w-10 rounded object-cover cursor-pointer hover:opacity-75"
                              />
                              <ZoomIn className="absolute h-3 w-3 top-1 right-1 text-white opacity-0 group-hover:opacity-100" />
                            </button>
                          ) : (
                            <div className="h-10 w-10 rounded bg-gray-200 flex items-center justify-center">
                              <ImageIcon className="h-5 w-5 text-gray-400" />
                            </div>
                          )}
                        </TableCell>
                        <TableCell className="font-medium">{record.jailLocation}</TableCell>
                        <TableCell className="font-medium">{record.cell}</TableCell>
                        <TableCell>{record.name}</TableCell>
                        <TableCell className="font-mono text-sm">{record.ocaNumber}</TableCell>
                        <TableCell>{record.arrestDateTime}</TableCell>
                        <TableCell className="text-xs max-w-xs truncate">{record.charges}</TableCell>
                        <TableCell>{getStatusBadge(record)}</TableCell>
                        <TableCell>
                          <div className="flex items-center space-x-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setEditingRecord(record)}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            {canDelete() && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleDelete(record.id)}
                                className="text-red-600 hover:text-red-700"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            )}
                          </div>
                        </TableCell>
                      </TableRow>
                      {expandedRecordId === record.id && (
                        <TableRow className="bg-gray-50 border-b border-gray-200">
                          <TableCell colSpan={9} className="py-3 px-6">
                            <div className="grid grid-cols-5 gap-4 text-sm">
                              <div>
                                <p className="font-semibold text-gray-600">DOB / Sex:</p>
                                <p>{formatDate(record.dob)} / {record.sexM ? 'M' : record.sexF ? 'F' : '-'}</p>
                              </div>
                              <div>
                                <p className="font-semibold text-gray-600">SSN:</p>
                                <p>{record.ssn || 'N/A'}</p>
                              </div>
                              <div>
                                <p className="font-semibold text-gray-600">Bond / Waiver:</p>
                                <p>{record.bond || 'N/A'} / {record.waiver || 'N/A'}</p>
                              </div>
                              <div>
                                <p className="font-semibold text-gray-600">Court Date:</p>
                                <p>{formatDate(record.courtDate) || 'N/A'}</p>
                              </div>
                              <div>
                                <p className="font-semibold text-gray-600">Release Date:</p>
                                <p>{record.releaseDateTime || 'N/A'}</p>
                              </div>
                              <div className="col-span-5">
                                <p className="font-semibold text-gray-600">Holders / Notes:</p>
                                <p className="text-xs italic">{record.holdersNotes || 'None'}</p>
                              </div>
                            </div>
                          </TableCell>
                        </TableRow>
                      )}
                    </React.Fragment>
                  ))}
                </TableBody>
              </Table>
            </div>

            {filteredData.length === 0 && (
              <div className="text-center py-8">
                <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No active inmates found matching your search criteria.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </TabsContent>

      <TabsContent value="released">
        <Card>
          <CardHeader>
            <CardTitle>Released Inmates / History ({filteredData.length})</CardTitle>
            <CardDescription>
              Historical records of released inmates
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[8%]">Photo</TableHead>
                    <TableHead className="w-[15%]">Name</TableHead>
                    <TableHead className="w-[10%]">OCA #</TableHead>
                    <TableHead className="w-[10%]">Arrest Date</TableHead>
                    <TableHead className="w-[10%]">Release Date</TableHead>
                    <TableHead className="w-[20%]">Charges</TableHead>
                    <TableHead className="w-[8%]">Location</TableHead>
                    <TableHead className="w-[10%]">Days Held</TableHead>
                    <TableHead className="w-[9%]">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredData.map((record) => {
                    const arrestDate = new Date(record.arrestDateTime)
                    const releaseDate = new Date(record.releaseDateTime)
                    const daysHeld = Math.ceil((releaseDate - arrestDate) / (1000 * 60 * 60 * 24))
                    
                    return (
                      <TableRow key={record.id} className="bg-white hover:bg-gray-50">
                        <TableCell>
                          {record.suspectPhotoBase64 ? (
                            <img
                              src={record.suspectPhotoBase64}
                              alt={record.name}
                              className="h-12 w-12 rounded object-cover cursor-pointer"
                              onClick={() => setSelectedPhotoRecord(record)}
                            />
                          ) : (
                            <div className="h-12 w-12 rounded bg-gray-200 flex items-center justify-center">
                              <User className="h-6 w-6 text-gray-400" />
                            </div>
                          )}
                        </TableCell>
                        <TableCell className="font-medium">{record.name}</TableCell>
                        <TableCell>{record.ocaNumber}</TableCell>
                        <TableCell>
                          {record.arrestDateTime ? new Date(record.arrestDateTime).toLocaleDateString() : 'N/A'}
                        </TableCell>
                        <TableCell>
                          {record.releaseDateTime ? new Date(record.releaseDateTime).toLocaleDateString() : 'N/A'}
                        </TableCell>
                        <TableCell className="max-w-xs truncate" title={record.charges}>
                          {record.charges}
                        </TableCell>
                        <TableCell>{record.jailLocation} {record.cell}</TableCell>
                        <TableCell>
                          <Badge variant="outline" className="bg-gray-100">
                            {daysHeld} {daysHeld === 1 ? 'day' : 'days'}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => setEditingRecord(record)}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleDelete(record.id)}
                              className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            </div>

            {filteredData.length === 0 && (
              <div className="text-center py-8">
                <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No released inmates found matching your search criteria.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>
      </main>

      {/* Photo Modal */}
      {selectedPhotoRecord && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={() => setSelectedPhotoRecord(null)}>
          <Card className="max-w-2xl w-full mx-4">
            <CardHeader>
              <CardTitle>{selectedPhotoRecord.name}</CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedPhotoRecord(null)}
                className="absolute right-4 top-4"
              >
                <X className="h-4 w-4" />
              </Button>
            </CardHeader>
            <CardContent>
              <img
                src={selectedPhotoRecord.suspectPhotoBase64}
                alt={selectedPhotoRecord.name}
                className="w-full rounded"
              />
            </CardContent>
          </Card>
        </div>
      )}

      {/* Email Modal */}
      {showEmailModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="max-w-md w-full mx-4">
            <CardHeader>
              <CardTitle>Send Report via Email</CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowEmailModal(false)}
                className="absolute right-4 top-4"
              >
                <X className="h-4 w-4" />
              </Button>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Email Address</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="recipient@example.com"
                    value={emailAddress}
                    onChange={(e) => setEmailAddress(e.target.value)}
                  />
                </div>
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setShowEmailModal(false)}>Cancel</Button>
                  <Button onClick={handleSendEmail} disabled={isSendingEmail}>
                    {isSendingEmail ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Mail className="h-4 w-4 mr-2" />}
                    Send Email
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}

function EditRecordForm({ record, onSave, onCancel, isAddMode }) {
  const [formData, setFormData] = useState(record || {})
  const [photoPreview, setPhotoPreview] = useState(record?.suspectPhotoBase64 || '')

  useEffect(() => {
    setFormData(record || {})
    setPhotoPreview(record?.suspectPhotoBase64 || '')
  }, [record])

  const handleSubmit = (e) => {
    e.preventDefault()
    onSave(formData)
  }

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handlePhotoUpload = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (event) => {
        const base64String = event.target?.result
        setPhotoPreview(base64String)
        handleChange('suspectPhotoBase64', base64String)
      }
      reader.readAsDataURL(file)
    }
  }

  if (!record) return null

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Photo Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Suspect Photo</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            {photoPreview && (
              <img src={photoPreview} alt="Preview" className="h-24 w-24 rounded object-cover" />
            )}
            <div className="flex-1">
              <Label htmlFor="photo" className="cursor-pointer">
                <div className="border-2 border-dashed border-gray-300 rounded p-4 text-center hover:border-blue-500">
                  <Upload className="h-6 w-6 mx-auto text-gray-400" />
                  <p className="text-sm text-gray-600 mt-2">Click to upload photo</p>
                </div>
              </Label>
              <Input
                id="photo"
                type="file"
                accept="image/*"
                onChange={handlePhotoUpload}
                className="hidden"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Inmate Details Section */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Inmate Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label htmlFor="jailLocation">Jail Location</Label>
              <Input
                id="jailLocation"
                value={formData.jailLocation || ''}
                onChange={(e) => handleChange('jailLocation', e.target.value)}
                placeholder="e.g., Solon"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                value={formData.name || ''}
                onChange={(e) => handleChange('name', e.target.value)}
                placeholder="Last, First Middle"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="dob">Date of Birth</Label>
              <Input
                id="dob"
                type="date"
                value={formData.dob || ''}
                onChange={(e) => handleChange('dob', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="ssn">SSN</Label>
              <Input
                id="ssn"
                value={formData.ssn || ''}
                onChange={(e) => handleChange('ssn', e.target.value)}
                placeholder="XXX-XX-XXXX"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="cell">Cell</Label>
              <Input
                id="cell"
                value={formData.cell || ''}
                onChange={(e) => handleChange('cell', e.target.value)}
                placeholder="e.g., SOL"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="ocaNumber">OCA Number</Label>
              <Input
                id="ocaNumber"
                value={formData.ocaNumber || ''}
                onChange={(e) => handleChange('ocaNumber', e.target.value)}
                placeholder="e.g., SHPD2025-02"
              />
            </div>
            <div className="space-y-2">
              <Label>Sex</Label>
              <div className="flex items-center space-x-4">
                <label className="flex items-center space-x-2">
                  <Checkbox
                    checked={formData.sexM || false}
                    onCheckedChange={(checked) => handleChange('sexM', checked)}
                  />
                  <span>Male</span>
                </label>
                <label className="flex items-center space-x-2">
                  <Checkbox
                    checked={formData.sexF || false}
                    onCheckedChange={(checked) => handleChange('sexF', checked)}
                  />
                  <span>Female</span>
                </label>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Custody & Charges Section */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Custody & Charges</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label htmlFor="arrestDateTime">Arrest Date/Time</Label>
              <Input
                id="arrestDateTime"
                type="datetime-local"
                value={formData.arrestDateTime || ''}
                onChange={(e) => handleChange('arrestDateTime', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Charge Type</Label>
              <div className="flex items-center space-x-4">
                <label className="flex items-center space-x-2">
                  <Checkbox
                    checked={formData.misdemeanor || false}
                    onCheckedChange={(checked) => handleChange('misdemeanor', checked)}
                  />
                  <span>Misdemeanor</span>
                </label>
                <label className="flex items-center space-x-2">
                  <Checkbox
                    checked={formData.felony || false}
                    onCheckedChange={(checked) => handleChange('felony', checked)}
                  />
                  <span>Felony</span>
                </label>
              </div>
            </div>
            <div className="space-y-2 lg:col-span-2">
              <Label htmlFor="charges">Charges</Label>
              <Textarea
                id="charges"
                value={formData.charges || ''}
                onChange={(e) => handleChange('charges', e.target.value)}
                placeholder="Enter charges..."
                rows={3}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Court & Release Details Section */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Court & Release Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label htmlFor="courtPacket">Court Packet</Label>
              <Input
                id="courtPacket"
                value={formData.courtPacket || ''}
                onChange={(e) => handleChange('courtPacket', e.target.value)}
                placeholder="Court packet info"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="courtCaseTicket">Court Case Ticket #</Label>
              <Input
                id="courtCaseTicket"
                value={formData.courtCaseTicket || ''}
                onChange={(e) => handleChange('courtCaseTicket', e.target.value)}
                placeholder="Ticket number"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="courtDate">Court Date</Label>
              <Input
                id="courtDate"
                type="date"
                value={formData.courtDate || ''}
                onChange={(e) => handleChange('courtDate', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="releaseDateTime">Release Date/Time</Label>
              <Input
                id="releaseDateTime"
                type="datetime-local"
                value={formData.releaseDateTime || ''}
                onChange={(e) => handleChange('releaseDateTime', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="bond">Bond</Label>
              <Input
                id="bond"
                value={formData.bond || ''}
                onChange={(e) => handleChange('bond', e.target.value)}
                placeholder="Bond amount"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="waiver">Waiver</Label>
              <Input
                id="waiver"
                value={formData.waiver || ''}
                onChange={(e) => handleChange('waiver', e.target.value)}
                placeholder="Waiver info"
              />
            </div>
            <div className="space-y-2 lg:col-span-2">
              <Label htmlFor="holdersNotes">Holders / Notes</Label>
              <Textarea
                id="holdersNotes"
                value={formData.holdersNotes || ''}
                onChange={(e) => handleChange('holdersNotes', e.target.value)}
                placeholder="Enter notes..."
                rows={2}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Form Actions */}
      <div className="flex justify-end space-x-2 pt-4">
        <Button type="button" variant="outline" onClick={onCancel}>Cancel</Button>
        <Button type="submit">{isAddMode ? 'Add Record' : 'Save Changes'}</Button>
      </div>
    </form>
  )
}

export default App
