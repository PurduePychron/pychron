
def main():
    info('Prepare for NP10 Blank analysis')
    close(description='Jan Inlet')
    open(description='Jan Ion Pump')
    close(description='Microbone to Minibone')
    open(description='Microbone to Turbo')
    open(description='Microbone to Inlet Pipette')
    close(description='Microbone to Getter NP-10C')
    open(description='Microbone to Getter NP-10H')
    
    close(description='CO2 Laser to Felix')
    close(description='CO2 Laser to Jan')
    close(description='Microbone to CO2 Laser')
    
    sleep(20)
