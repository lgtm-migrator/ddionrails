# Generated by Django 2.2 on 2019-05-14 15:32                                           
                                                                                        
from django.db import migrations, models                                                
                                                                                        
                                                                                        
class Migration(migrations.Migration):                                                  
                                                                                        
    dependencies = [                                                                    
        ('instruments', '0001_initial'),                                                
    ]                                                                                   
                                                                                        
    operations = [                                                                      
        migrations.AlterField(                                                          
            model_name='question',                                                      
            name='label',                                                               
            field=models.TextField(blank=True),                                         
        ),                                                                              
        migrations.AlterField(                                                          
            model_name='question',                                                      
            name='label_de',                                                            
            field=models.TextField(blank=True),                                         
        ),                                                                              
    ]    