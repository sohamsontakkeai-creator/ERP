import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, Calendar, IndianRupee, RefreshCw, Users, Clock } from 'lucide-react';
import { API_BASE } from '@/lib/api';
import { toast } from '@/components/ui/use-toast';
import { useAutoRefresh } from '@/hooks/useAutoRefresh';
import { AutoRefreshIndicator } from '@/components/AutoRefreshIndicator';

const ManagementAlerts = () => {
  const [onLeaveToday, setOnLeaveToday] = useState([]);
  const [pendingPayments, setPendingPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      // Fetch employees on leave today
      await fetchOnLeaveToday();
      
      // Fetch pending payment reminders
      await fetchPendingPayments();
    } catch (error) {
      console.error('Error fetching alerts:', error);
      toast({
        title: 'Error',
        description: 'Failed to load management alerts',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchOnLeaveToday = async () => {
    try {
      const response = await fetch(`${API_BASE}/hr/leaves`);
      if (response.ok) {
        const data = await response.json();
        // Handle both array and object with leaves property
        const leaves = Array.isArray(data) ? data : (data.leaves || []);
        
        // Filter leaves that are approved and include the selected date
        const selectedLeaves = leaves.filter(leave => {
          if (leave.status !== 'approved') return false;
          const startDate = leave.startDate.split('T')[0];
          const endDate = leave.endDate.split('T')[0];
          return startDate <= selectedDate && endDate >= selectedDate;
        });
        
        setOnLeaveToday(selectedLeaves);
      }
    } catch (error) {
      console.error('Error fetching leaves:', error);
      setOnLeaveToday([]); // Set empty array on error
    }
  };

  // Refetch when selected date changes
  useEffect(() => {
    if (!loading) {
      fetchOnLeaveToday();
    }
  }, [selectedDate]);

  const fetchPendingPayments = async () => {
    try {
      const response = await fetch(`${API_BASE}/sales/payment-reminders`);
      if (response.ok) {
        const data = await response.json();
        console.log('Payment reminders data:', data); // Debug log
        // Handle both array and object with reminders property
        const reminders = Array.isArray(data) ? data : (data.reminders || []);
        console.log('Reminders array:', reminders); // Debug log
        // Show ALL pending payment reminders (not just overdue)
        setPendingPayments(reminders);
      }
    } catch (error) {
      console.error('Error fetching payment reminders:', error);
      setPendingPayments([]); // Set empty array on error
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  // Auto-refresh every 10 seconds
  const { isRefreshing: autoRefreshing, lastRefreshTime, isPaused } = useAutoRefresh(
    fetchAlerts,
    10000,
    { enabled: true, pauseOnInput: true, pauseOnModal: true }
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-800 text-lg font-medium">Loading Alerts...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <AutoRefreshIndicator 
        isRefreshing={autoRefreshing}
        lastRefreshTime={lastRefreshTime}
        isPaused={isPaused}
      />
      {/* On Leave Section with Date Picker */}
      <Card className="border-2 border-blue-200 shadow-lg">
        <CardHeader className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Users className="h-6 w-6" />
              Employees On Leave
            </CardTitle>
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="px-3 py-1 rounded border border-white/30 bg-white/20 text-white text-sm focus:outline-none focus:ring-2 focus:ring-white/50"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-6">
          {onLeaveToday.length === 0 ? (
            <div className="text-center p-8 bg-gray-50 rounded-lg">
              <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600 font-medium">
                No employees on leave on {new Date(selectedDate).toLocaleDateString()}
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto border border-gray-200 rounded-lg">
              <table className="w-full bg-white">
                <thead className="bg-gray-100">
                  <tr className="border-b border-gray-300">
                    <th className="p-3 text-left text-gray-900 font-bold">Employee Name</th>
                    <th className="p-3 text-left text-gray-900 font-bold">Leave Type</th>
                    <th className="p-3 text-left text-gray-900 font-bold">Start Date</th>
                    <th className="p-3 text-left text-gray-900 font-bold">End Date</th>
                    <th className="p-3 text-left text-gray-900 font-bold">Days</th>
                    <th className="p-3 text-left text-gray-900 font-bold">Reason</th>
                  </tr>
                </thead>
                <tbody className="bg-white">
                  {onLeaveToday.map((leave) => (
                    <tr key={leave.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="p-3 text-gray-900 font-medium">{leave.employeeName}</td>
                      <td className="p-3">
                        <Badge className="capitalize bg-blue-100 text-blue-800">
                          {leave.leaveType}
                        </Badge>
                      </td>
                      <td className="p-3 text-gray-700">
                        {new Date(leave.startDate).toLocaleDateString()}
                      </td>
                      <td className="p-3 text-gray-700">
                        {new Date(leave.endDate).toLocaleDateString()}
                      </td>
                      <td className="p-3 text-gray-700">{leave.daysRequested} days</td>
                      <td className="p-3 text-gray-600 text-sm">{leave.reason || 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pending Payment Reminders Section */}
      <Card className="border-2 border-red-200 shadow-lg">
        <CardHeader className="bg-gradient-to-r from-red-600 to-orange-600 text-white">
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-6 w-6" />
            Pending Payment Reminders
            {pendingPayments.length > 0 && (
              <Badge className="ml-2 bg-white text-red-600 font-bold">
                {pendingPayments.filter(r => r.status === 'overdue').length} Overdue / {pendingPayments.length} Total
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          {pendingPayments.length === 0 ? (
            <div className="text-center p-8 bg-gray-50 rounded-lg">
              <IndianRupee className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600 font-medium">No pending payment reminders</p>
            </div>
          ) : (
            <div className="overflow-x-auto border border-gray-200 rounded-lg">
              <table className="w-full bg-white">
                <thead className="bg-gray-100">
                  <tr className="border-b border-gray-300">
                    <th className="p-3 text-left text-gray-900 font-bold">Order #</th>
                    <th className="p-3 text-left text-gray-900 font-bold">Customer</th>
                    <th className="p-3 text-left text-gray-900 font-bold">Order Amount</th>
                    <th className="p-3 text-left text-gray-900 font-bold">Due Date</th>
                    <th className="p-3 text-left text-gray-900 font-bold">Days Overdue</th>
                    <th className="p-3 text-left text-gray-900 font-bold">Status</th>
                  </tr>
                </thead>
                <tbody className="bg-white">
                  {pendingPayments.map((reminder) => (
                    <tr key={reminder.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="p-3 text-gray-900 font-medium">#{reminder.orderNumber}</td>
                      <td className="p-3 text-gray-900">{reminder.customerName}</td>
                      <td className="p-3 text-gray-900 font-bold">
                        ₹{reminder.finalAmount?.toLocaleString() || reminder.final_amount?.toLocaleString() || reminder.totalAmount?.toLocaleString() || reminder.total_amount?.toLocaleString() || '0'}
                      </td>
                      <td className="p-3 text-gray-700">
                        {new Date(reminder.paymentDueDate || reminder.payment_due_date).toLocaleDateString()}
                      </td>
                      <td className="p-3">
                        <Badge className={`${
                          reminder.daysUntilDue < 0
                            ? 'bg-red-100 text-red-800' 
                            : reminder.daysUntilDue === 0
                            ? 'bg-orange-100 text-orange-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {reminder.daysUntilDue < 0 
                            ? `${Math.abs(reminder.daysUntilDue)} days overdue`
                            : reminder.daysUntilDue === 0
                            ? 'Due today'
                            : `${reminder.daysUntilDue} days remaining`
                          }
                        </Badge>
                      </td>
                      <td className="p-3">
                        <Badge className={`flex items-center gap-1 w-fit ${
                          reminder.status === 'overdue' 
                            ? 'bg-red-100 text-red-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          <Clock className="h-3 w-3" />
                          {reminder.status === 'overdue' ? 'Overdue' : 'Pending'}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="border-2 border-blue-200 bg-white">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 font-medium">Employees on Leave</p>
                <p className="text-3xl font-bold text-blue-600">{onLeaveToday.length}</p>
              </div>
              <Users className="h-12 w-12 text-blue-600 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-2 border-red-200 bg-white">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 font-medium">Pending Payments</p>
                <p className="text-3xl font-bold text-red-600">{pendingPayments.length}</p>
                <p className="text-xs text-gray-500 mt-1">
                  {pendingPayments.filter(r => r.status === 'overdue').length} overdue
                </p>
              </div>
              <AlertCircle className="h-12 w-12 text-red-600 opacity-20" />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ManagementAlerts;
