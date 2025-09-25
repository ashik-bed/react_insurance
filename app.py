import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

// -------------------
// Types
// -------------------
type UserRole = "admin" | "AGM" | "manager" | "branch";

interface User {
  username: string;
  password_b64: string;
  role: UserRole;
  assigned_branches: string[];
  created_by: string;
  created_at: string;
}

interface Customer {
  customer_id: string;
  name: string;
  phone: string;
  aadhaar_number: string;
  email: string;
  branch: string;
  submitted_by: string;
  status: "submitted" | "approved_by_manager" | "approved_by_agm";
  document_path: string;
  created_at: string;
  updated_at: string;
}

interface DashboardContent {
  text: string;
  image_path: string | null;
}

// -------------------
// Helpers
// -------------------
const hashPassword = (pw: string) => btoa(pw);
const checkPassword = (pw: string, hashed: string) => btoa(pw) === hashed;

const generateCustomerId = () => {
  const ts = new Date().getTime();
  const rnd = Math.floor(Math.random() * 1000)
    .toString()
    .padStart(3, "0");
  return `CUST-${ts}${rnd}`;
};

const statusLabels = {
  submitted: { text: "Submitted", color: "text-red-600", icon: "🔴" },
  approved_by_manager: {
    text: "Manager Approved",
    color: "text-yellow-600",
    icon: "🟡",
  },
  approved_by_agm: {
    text: "AGM Approved",
    color: "text-green-600",
    icon: "🟢",
  },
};

// -------------------
// Main Component
// -------------------
const CRMApp: React.FC = () => {
  const [users, setUsers] = useState<Record<string, User>>({});
  const [customers, setCustomers] = useState<Record<string, Customer>>({});
  const [loggedIn, setLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [activePage, setActivePage] = useState<string | null>(null);
  const [dashboardContent, setDashboardContent] = useState<DashboardContent>({
    text: "Welcome to CRM System. Please login to continue.",
    image_path: null,
  });

  const [loginForm, setLoginForm] = useState({ username: "", password: "" });
  const [newUserForm, setNewUserForm] = useState({
    username: "",
    password: "",
    assignedBranches: "",
    role: "AGM" as UserRole,
  });
  const [customerForm, setCustomerForm] = useState({
    name: "",
    phone: "",
    aadhaar: "",
    email: "",
    file: null as File | null,
  });
  const [searchText, setSearchText] = useState("");

  // -------------------
  // Persistence
  // -------------------
  useEffect(() => {
    const savedUsers = localStorage.getItem("crm_users");
    const savedCustomers = localStorage.getItem("crm_customers");
    const savedDashboard = localStorage.getItem("crm_dashboard");

    if (savedUsers) setUsers(JSON.parse(savedUsers));
    if (savedCustomers) setCustomers(JSON.parse(savedCustomers));
    if (savedDashboard) setDashboardContent(JSON.parse(savedDashboard));
  }, []);

  useEffect(() => localStorage.setItem("crm_users", JSON.stringify(users)), [users]);
  useEffect(() => localStorage.setItem("crm_customers", JSON.stringify(customers)), [customers]);
  useEffect(() => localStorage.setItem("crm_dashboard", JSON.stringify(dashboardContent)), [dashboardContent]);

  // -------------------
  // Initial Admin User
  // -------------------
  useEffect(() => {
    if (!users.ASHIK) {
      const adminUser: User = {
        username: "ASHIK",
        password_b64: btoa("ASHph7#"),
        role: "admin",
        assigned_branches: [],
        created_by: "system",
        created_at: new Date().toISOString(),
      };
      setUsers((prev) => ({ ...prev, ASHIK: adminUser }));
    }
  }, [users]);

  // -------------------
  // Auth
  // -------------------
  const handleLogin = () => {
    const user = users[loginForm.username];
    if (user && checkPassword(loginForm.password, user.password_b64)) {
      setLoggedIn(true);
      setCurrentUser(user);
      setActivePage(null);
    } else {
      alert("Invalid credentials. Please try again.");
    }
  };

  const handleLogout = () => {
    setLoggedIn(false);
    setCurrentUser(null);
    setActivePage(null);
  };

  // -------------------
  // User Management
  // -------------------
  const createUser = () => {
    if (!newUserForm.username.trim()) return alert("Username is required");
    if (users[newUserForm.username]) return alert("Username already exists");
    if (newUserForm.password.length < 6)
      return alert("Password must be at least 6 characters");

    const branches = newUserForm.assignedBranches
      .split(",")
      .map((b) => b.trim())
      .filter(Boolean);

    const newUser: User = {
      username: newUserForm.username,
      password_b64: hashPassword(newUserForm.password),
      role: newUserForm.role,
      assigned_branches: branches,
      created_by: currentUser?.username || "system",
      created_at: new Date().toISOString(),
    };

    setUsers((prev) => ({ ...prev, [newUser.username]: newUser }));
    setNewUserForm({ username: "", password: "", assignedBranches: "", role: "AGM" });
    alert("User created successfully");
  };

  // -------------------
  // Customer Management
  // -------------------
  const addCustomer = () => {
    if (!customerForm.name || !customerForm.phone || !customerForm.aadhaar || !customerForm.file)
      return alert("All fields are required");
    if (!/^\d{10}$/.test(customerForm.phone)) return alert("Phone number must be 10 digits");
    if (!/^\d{12}$/.test(customerForm.aadhaar)) return alert("Aadhaar must be 12 digits");
    if (customerForm.email && !customerForm.email.includes("@")) return alert("Invalid email");

    const customerId = generateCustomerId();
    const branch = currentUser?.assigned_branches[0] || currentUser?.username || "";

    const newCustomer: Customer = {
      customer_id: customerId,
      name: customerForm.name,
      phone: customerForm.phone,
      aadhaar_number: customerForm.aadhaar,
      email: customerForm.email,
      branch,
      submitted_by: currentUser?.username || "",
      status: "submitted",
      document_path: URL.createObjectURL(customerForm.file),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    setCustomers((prev) => ({ ...prev, [customerId]: newCustomer }));
    setCustomerForm({ name: "", phone: "", aadhaar: "", email: "", file: null });
    alert("Customer submitted successfully");
  };

  const updateCustomerStatus = (id: string, status: Customer["status"]) => {
    setCustomers((prev) => ({
      ...prev,
      [id]: { ...prev[id], status, updated_at: new Date().toISOString() },
    }));
  };

  const deleteCustomer = (id: string) => {
    setCustomers((prev) => {
      const copy = { ...prev };
      delete copy[id];
      return copy;
    });
  };

  const getCustomersForUser = () => {
    let list = Object.values(customers);

    if (searchText) {
      list = list.filter(
        (c) =>
          c.name.toLowerCase().includes(searchText.toLowerCase()) ||
          c.customer_id.toLowerCase().includes(searchText.toLowerCase())
      );
    }

    if (currentUser?.role === "branch") {
      list = list.filter((c) => c.submitted_by === currentUser.username);
    } else if (currentUser?.role === "manager") {
      list = list.filter((c) => currentUser.assigned_branches.includes(c.branch));
    }

    return list;
  };

  // -------------------
  // Views
  // -------------------
  if (!loggedIn) {
    return (
      <div className="min-h-screen bg-background p-4">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold text-center text-maroon mb-8">DASHBOARD</h1>

          {dashboardContent.image_path && (
            <img
              src={dashboardContent.image_path}
              alt="CRM Dashboard Banner"
              className="w-full h-auto rounded-lg mb-6"
            />
          )}

          <Card className="max-w-md mx-auto">
            <CardHeader>
              <CardTitle className="text-center">Login</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  placeholder="Enter username"
                  value={loginForm.username}
                  onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Enter password"
                  value={loginForm.password}
                  onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                />
              </div>
              <Button className="w-full" onClick={handleLogin}>
                Login
              </Button>
            </CardContent>
          </Card>

          <p className="text-center mt-6 text-muted-foreground">{dashboardContent.text}</p>
        </div>
      </div>
    );
  }

  const menuOptions =
    currentUser?.role === "branch"
      ? ["Submit Customer", "Customer Records"]
      : ["Create User", "Customer Records", ...(currentUser.role === "admin" ? ["Admin Settings"] : [])];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-primary text-primary-foreground p-4">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">DASHBOARD</h1>
          <div className="flex items-center space-x-4">
            <Avatar>
              <AvatarFallback>{currentUser?.username.charAt(0)}</AvatarFallback>
            </Avatar>
            <span>{currentUser?.username} | {currentUser?.role}</span>
            <Button variant="ghost" onClick={handleLogout}>➜</Button>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-muted p-4">
        <div className="max-w-6xl mx-auto flex space-x-4">
          {menuOptions.map((opt) => (
            <Button
              key={opt}
              variant={activePage === opt ? "default" : "outline"}
              onClick={() => setActivePage(opt)}
            >
              {opt}
            </Button>
          ))}
        </div>
      </nav>

      {/* Pages */}
      <main className="max-w-6xl mx-auto p-4 space-y-6">
        {/* Create User */}
        {activePage === "Create User" && ["admin", "AGM", "manager"].includes(currentUser!.role) && (
          <Card>
            <CardHeader><CardTitle>Create User</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label>Username</Label>
                  <Input
                    value={newUserForm.username}
                    onChange={(e) => setNewUserForm({ ...newUserForm, username: e.target.value })}
                  />
                </div>
                <div>
                  <Label>Password</Label>
                  <Input
                    type="password"
                    value={newUserForm.password}
                    onChange={(e) => setNewUserForm({ ...newUserForm, password: e.target.value })}
                  />
                </div>
              </div>

              {currentUser?.role !== "branch" && (
                <div>
                  <Label>Assign Branches (comma separated)</Label>
                  <Input
                    value={newUserForm.assignedBranches}
                    onChange={(e) =>
                      setNewUserForm({ ...newUserForm, assignedBranches: e.target.value })
                    }
                  />
                </div>
              )}

              <div>
                <Label>Role</Label>
                <Select
                  value={newUserForm.role}
                  onValueChange={(v) => setNewUserForm({ ...newUserForm, role: v as UserRole })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select role" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="AGM">AGM</SelectItem>
                    <SelectItem value="manager">Manager</SelectItem>
                    <SelectItem value="branch">Branch</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Button onClick={createUser}>Create User</Button>
            </CardContent>
          </Card>
        )}

        {/* Submit Customer */}
        {activePage === "Submit Customer" && currentUser?.role === "branch" && (
          <Card>
            <CardHeader><CardTitle>Submit Customer</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input placeholder="Name" value={customerForm.name} onChange={(e) => setCustomerForm({ ...customerForm, name: e.target.value })} />
                <Input placeholder="Phone" value={customerForm.phone} onChange={(e) => setCustomerForm({ ...customerForm, phone: e.target.value })} />
                <Input placeholder="Aadhaar" value={customerForm.aadhaar} onChange={(e) => setCustomerForm({ ...customerForm, aadhaar: e.target.value })} />
                <Input placeholder="Email" value={customerForm.email} onChange={(e) => setCustomerForm({ ...customerForm, email: e.target.value })} />
              </div>
              <Input type="file" onChange={(e) => setCustomerForm({ ...customerForm, file: e.target.files?.[0] || null })} />
              <Button onClick={addCustomer}>Submit</Button>
            </CardContent>
          </Card>
        )}

        {/* Customer Records */}
        {activePage === "Customer Records" && (
          <Card>
            <CardHeader className="flex flex-col md:flex-row md:justify-between items-start md:items-center space-y-2 md:space-y-0">
              <CardTitle>Customer Records</CardTitle>
              <Input
                placeholder="Search by Name or ID"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                className="max-w-sm"
              />
            </CardHeader>
            <CardContent>
              {getCustomersForUser().length ? (
                <div className="overflow-x-auto">
                  <table className="w-full table-auto border-collapse">
                    <thead>
                      <tr className="border-b">
                        <th className="p-2 text-left">ID</th>
                        <th className="p-2 text-left">Name</th>
                        <th className="p-2 text-left">Phone</th>
                        <th className="p-2 text-left">Aadhaar</th>
                        <th className="p-2 text-left">Email</th>
                        <th className="p-2 text-left">Branch</th>
                        <th className="p-2 text-left">Status</th>
                        <th className="p-2 text-left">Document</th>
                        <th className="p-2 text-left">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {getCustomersForUser().map((c) => (
                        <tr key={c.customer_id} className="border-b">
                          <td className="p-2">{c.customer_id}</td>
                          <td className="p-2">{c.name}</td>
                          <td className="p-2">{c.phone}</td>
                          <td className="p-2">{c.aadhaar_number}</td>
                          <td className="p-2">{c.email}</td>
                          <td className="p-2">{c.branch}</td>
                          <td className={`p-2 ${statusLabels[c.status].color}`}>
                            {statusLabels[c.status].icon} {statusLabels[c.status].text}
                          </td>
                          <td className="p-2">
                            {c.document_path && (
                              <a href={c.document_path} download className="text-blue-600 hover:underline">📄 Download</a>
                            )}
                          </td>
                          <td className="p-2 space-x-2">
                            {c.status === "submitted" && currentUser?.role === "manager" && (
                              <Button size="sm" onClick={() => updateCustomerStatus(c.customer_id, "approved_by_manager")}>Approve</Button>
                            )}
                            {c.status === "approved_by_manager" && currentUser?.role === "AGM" && (
                              <Button size="sm" onClick={() => updateCustomerStatus(c.customer_id, "approved_by_agm")}>Approve</Button>
                            )}
                            <Button variant="destructive" size="sm" onClick={() => deleteCustomer(c.customer_id)}>Delete</Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-muted-foreground">No records found.</p>
              )}
            </CardContent>
          </Card>
        )}

        {/* Admin Settings */}
        {activePage === "Admin Settings" && currentUser?.role === "admin" && (
          <Card>
            <CardHeader><CardTitle>Admin Settings</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="dashboard-text">Dashboard Text</Label>
                <Textarea
                  id="dashboard-text"
                  value={dashboardContent.text}
                  onChange={(e) =>
                    setDashboardContent({ ...dashboardContent, text: e.target.value })
                  }
                  placeholder="Enter dashboard welcome text"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="dashboard-image">Dashboard Image</Label>
                <Input
                  id="dashboard-image"
                  type="file"
                  accept="image/*"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) {
                      const url = URL.createObjectURL(file);
                      setDashboardContent({ ...dashboardContent, image_path: url });
                    }
                  }}
                />
              </div>
              <Button onClick={() => alert("Dashboard content updated successfully")}>
                Update Dashboard
              </Button>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
};

export default CRMApp;
