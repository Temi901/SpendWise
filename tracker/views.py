from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Transaction, Budget
from .forms import TransactionForm, BudgetForm
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import csv
import io
from datetime import datetime

@login_required(login_url='/accounts/login/')
def dashboard(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    balance = total_income - total_expenses

    # Data for charts
    categories = {}
    for t in transactions:
        if t.transaction_type == 'expense':
            if t.category in categories:
                categories[t.category] += float(t.amount)
            else:
                categories[t.category] = float(t.amount)

    category_labels = list(categories.keys())
    category_data = list(categories.values())

    # Budget Goals
    budgets = Budget.objects.filter(user=request.user)
    
    budget_data = []
    for budget in budgets:
        spent = sum(
            float(t.amount) for t in transactions
            if t.category.lower() == budget.category.lower()
            and t.transaction_type == 'expense'
        )
        percentage = (spent / float(budget.amount)) * 100 if budget.amount > 0 else 0
        budget_data.append({
    'id': budget.pk,
    'category': budget.category,
    'budget': float(budget.amount),
    'spent': spent,
    'percentage': min(percentage, 100),
    'exceeded': percentage > 100,
    'warning': 75 <= percentage <= 100,
})

    form = TransactionForm()
    budget_form = BudgetForm()

    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'form': form,
        'budget_form': budget_form,
        'budget_data': budget_data,
        'category_labels': category_labels,
        'category_data': category_data,
    }

    return render(request, 'tracker/dashboard.html', context)


def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('dashboard')
    return redirect('dashboard')


def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    transaction.delete()
    return redirect('dashboard')


def edit_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TransactionForm(instance=transaction)
    
    return render(request, 'tracker/edit.html', {'form': form, 'transaction': transaction})


def add_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            return redirect('dashboard')
    return redirect('dashboard')


def delete_budget(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    budget.delete()
    return redirect('dashboard')

@login_required(login_url='/accounts/login/')
def export_pdf(request):
    # Create HTTP response with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="SpendWise_Report.pdf"'

    # Create PDF document
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    title = Paragraph("💰 SpendWise Transaction Report", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.3 * inch))

    # Summary
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    balance = total_income - total_expenses

    summary_data = [
        ['Total Income', 'Total Expenses', 'Balance'],
        [f'₦{total_income}', f'₦{total_expenses}', f'₦{balance}'],
    ]

    summary_table = Table(summary_data, colWidths=[2 * inch, 2 * inch, 2 * inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f2f5')),
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Transactions heading
    elements.append(Paragraph("Transaction History", styles['Heading2']))
    elements.append(Spacer(1, 0.2 * inch))

    # Transactions table
    table_data = [['Title', 'Amount', 'Category', 'Type', 'Date']]

    for t in transactions:
        table_data.append([
            t.title,
            f'₦{t.amount}',
            t.category,
            t.transaction_type.capitalize(),
            str(t.date),
        ])

    trans_table = Table(table_data, colWidths=[2*inch, 1.2*inch, 1.2*inch, 1*inch, 1.1*inch])
    trans_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), 
         [colors.HexColor('#ffffff'), colors.HexColor('#f8f9fa')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
    ]))

    elements.append(trans_table)

    # Build PDF
    doc.build(elements)
    return response

@login_required(login_url='/accounts/login/')
def import_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        # Check if it's a CSV file
        if not csv_file.name.endswith('.csv'):
            return render(request, 'tracker/import_csv.html', {
                'error': 'Please upload a CSV file!'
            })
        
        # Read the file
        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        next(io_string)  # Skip header row
        
        imported = 0
        errors = 0
        
        for column in csv.reader(io_string, delimiter=','):
            try:
                # Expected format: Date, Title, Amount, Type, Category
                Transaction.objects.create(
                    user=request.user,
                    date=column[0].strip(),
                    title=column[1].strip(),
                    amount=float(column[2].strip().replace(',', '')),
                    transaction_type='income' if column[3].strip().lower() in ['credit', 'income'] else 'expense',
                    category=column[4].strip() if len(column) > 4 else 'Other',
                )
                imported += 1
            except Exception:
                errors += 1
                continue
        
        return render(request, 'tracker/import_csv.html', {
            'success': f'Successfully imported {imported} transactions!',
            'errors': f'{errors} rows skipped due to errors.' if errors > 0 else None
        })
    
    return render(request, 'tracker/import_csv.html')