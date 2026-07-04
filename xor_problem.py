import torch
import torch.nn as nn
import torch.optim as optim
import json

# This is the intentionally weak baseline architecture.
# It is purely linear, so it mathematically CANNOT solve the XOR problem.
# The Multi-Agent Orchestrator must recognize this and mutate it!
class XORModel(nn.Module):
    def __init__(self):
        super(XORModel, self).__init__()
        self.fc1 = nn.Linear(2, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        return self.sigmoid(self.fc1(x))

if __name__ == "__main__":
    # The XOR Dataset
    X = torch.tensor([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
    y = torch.tensor([[0.0], [1.0], [1.0], [0.0]])

    model = XORModel()
    criterion = nn.BCELoss()
    
    # Load Hyperparameters
    try:
        with open('hyperparameters.json', 'r') as f:
            hyper = json.load(f)
            lr = hyper.get("learning_rate", 0.01)
            epochs = hyper.get("epochs", 1000)
    except:
        lr = 0.01
        epochs = 1000

    optimizer = optim.Adam(model.parameters(), lr=lr)

    # Training Loop
    for epoch in range(epochs):
        optimizer.zero_grad()
        outputs = model(X)
        loss = criterion(outputs, y)
        loss.backward()
        optimizer.step()

    print(f"Final Loss: {loss.item():.4f}")
