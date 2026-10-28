# TODO: Implement Simultaneous Order Confirmation Page Opening and Email Sending

## Tasks
- [ ] Modify checkout view to handle AJAX order processing
- [ ] Add new URL for AJAX order submission
- [ ] Update checkout.html template to use AJAX submission
- [ ] Test the checkout process to ensure confirmation page opens in new tab and email is sent
- [ ] Verify email functionality works correctly

## Details
- Current checkout process: Form submits POST to checkout view, which creates order, sends email, and renders confirmation template
- New requirement: After clicking "Place Order", open confirmation page in new tab simultaneously while processing order and sending email
- Approach: Use AJAX to submit order, get order ID in response, then open confirmation page in new tab
