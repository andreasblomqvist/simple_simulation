import React, { useState } from 'react'
import { 
  Input,
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
  PasswordInput,
  SearchInput,
  FormField,
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle
} from '../ui'
import { User, Mail, DollarSign, Calendar, Building } from 'lucide-react'

export const InputSystemDemo: React.FC = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    search: '',
    salary: '',
    website: '',
    startDate: ''
  })
  
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [success, setSuccess] = useState<Record<string, string>>({})

  const handleChange = (field: string) => (value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
    
    // Simple validation example
    if (field === 'email' && value) {
      const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)
      if (isValid) {
        setSuccess(prev => ({ ...prev, email: 'Valid email format' }))
      } else {
        setErrors(prev => ({ ...prev, email: 'Please enter a valid email address' }))
      }
    }
    
    if (field === 'confirmPassword' && value !== formData.password) {
      setErrors(prev => ({ ...prev, confirmPassword: 'Passwords do not match' }))
    } else if (field === 'confirmPassword') {
      setSuccess(prev => ({ ...prev, confirmPassword: 'Passwords match' }))
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold">Enhanced Input System Demo</h1>
        <p className="text-muted-foreground">
          Comprehensive input components with validation states, sizes, and accessibility
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Size Variants */}
        <Card>
          <CardHeader>
            <CardTitle>Size Variants</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <FormField label="Small Input" helperText="Size: sm">
              <Input size="sm" placeholder="Small input field" />
            </FormField>
            
            <FormField label="Medium Input (Default)" helperText="Size: md">
              <Input size="md" placeholder="Medium input field" />
            </FormField>
            
            <FormField label="Large Input" helperText="Size: lg">
              <Input size="lg" placeholder="Large input field" />
            </FormField>
          </CardContent>
        </Card>

        {/* Validation States */}
        <Card>
          <CardHeader>
            <CardTitle>Validation States</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <FormField 
              label="Default State" 
              helperText="Normal input field"
            >
              <Input placeholder="Type something..." />
            </FormField>
            
            <FormField 
              label="Error State" 
              error="This field is required"
            >
              <Input 
                placeholder="This field has an error" 
                state="error"
              />
            </FormField>
            
            <FormField 
              label="Success State" 
              success="Input is valid"
            >
              <Input 
                placeholder="This field is valid" 
                state="success"
              />
            </FormField>
            
            <FormField 
              label="Warning State" 
              helperText="Warning: Consider reviewing this"
            >
              <Input 
                placeholder="This field has a warning" 
                state="warning"
              />
            </FormField>
          </CardContent>
        </Card>

        {/* Icon Support */}
        <Card>
          <CardHeader>
            <CardTitle>Icon Support</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <FormField label="Left Icon" helperText="Icon on the left">
              <Input 
                leftIcon={<User className="h-4 w-4" />}
                placeholder="Username"
              />
            </FormField>
            
            <FormField label="Right Icon" helperText="Icon on the right">
              <Input 
                rightIcon={<Mail className="h-4 w-4" />}
                placeholder="Email address"
              />
            </FormField>
            
            <FormField label="Loading State" helperText="Shows spinner">
              <Input 
                loading
                placeholder="Loading..."
              />
            </FormField>
          </CardContent>
        </Card>

        {/* Specialized Components */}
        <Card>
          <CardHeader>
            <CardTitle>Specialized Components</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <FormField 
              label="Password Input" 
              helperText="Click the eye icon to toggle visibility"
            >
              <PasswordInput 
                placeholder="Enter your password"
                value={formData.password}
                onValueChange={handleChange('password')}
              />
            </FormField>
            
            <FormField 
              label="Confirm Password" 
              error={errors.confirmPassword}
              success={success.confirmPassword}
            >
              <PasswordInput 
                placeholder="Confirm your password"
                value={formData.confirmPassword}
                onValueChange={handleChange('confirmPassword')}
                error={errors.confirmPassword}
                success={success.confirmPassword}
              />
            </FormField>
            
            <FormField 
              label="Search Input" 
              helperText="Type to search, clear button appears"
            >
              <SearchInput 
                placeholder="Search users, projects, files..."
                value={formData.search}
                onValueChange={handleChange('search')}
                onSearch={(value) => console.log('Searching for:', value)}
                onClear={() => console.log('Search cleared')}
              />
            </FormField>
          </CardContent>
        </Card>

        {/* Input Groups */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Input Groups</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <FormField 
              label="Salary Range" 
              helperText="Currency prefix with input"
            >
              <InputGroup>
                <InputGroupAddon>
                  <DollarSign className="h-4 w-4" />
                </InputGroupAddon>
                <InputGroupInput 
                  type="number"
                  placeholder="50000"
                  value={formData.salary}
                  onValueChange={handleChange('salary')}
                />
                <InputGroupAddon>USD</InputGroupAddon>
              </InputGroup>
            </FormField>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField 
                label="Website URL" 
                helperText="URL with prefix"
              >
                <InputGroup>
                  <InputGroupAddon>https://</InputGroupAddon>
                  <InputGroupInput 
                    placeholder="example.com"
                    value={formData.website}
                    onValueChange={handleChange('website')}
                  />
                </InputGroup>
              </FormField>
              
              <FormField 
                label="Office Location" 
                helperText="Location with icon"
              >
                <InputGroup>
                  <InputGroupAddon>
                    <Building className="h-4 w-4" />
                  </InputGroupAddon>
                  <InputGroupInput placeholder="New York, NY" />
                </InputGroup>
              </FormField>
            </div>
          </CardContent>
        </Card>

        {/* Complete Form Example */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Complete Form Example</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField 
                label="Full Name" 
                required 
                helperText="Enter your first and last name"
              >
                <Input 
                  leftIcon={<User className="h-4 w-4" />}
                  placeholder="John Doe"
                  value={formData.name}
                  onValueChange={handleChange('name')}
                />
              </FormField>
              
              <FormField 
                label="Email Address" 
                required
                error={errors.email}
                success={success.email}
              >
                <Input 
                  type="email"
                  leftIcon={<Mail className="h-4 w-4" />}
                  placeholder="john@example.com"
                  value={formData.email}
                  onValueChange={handleChange('email')}
                  error={errors.email}
                  success={success.email}
                />
              </FormField>
            </div>
            
            <FormField 
              label="Start Date" 
              helperText="When do you want to begin?"
              layout="horizontal"
              labelWidth="120px"
            >
              <Input 
                type="date"
                leftIcon={<Calendar className="h-4 w-4" />}
                value={formData.startDate}
                onValueChange={handleChange('startDate')}
              />
            </FormField>
            
            <div className="flex gap-4 pt-4">
              <Button variant="primary" size="lg">
                Submit Form
              </Button>
              <Button variant="secondary" size="lg">
                Reset
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default InputSystemDemo