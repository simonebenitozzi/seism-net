/*
offset cancellation example
This example automatically finds offset values for each axis of the
accelerometer and gyroscope.

NOTE: Please don't move the sensor while offset is adjusted.

NOTE2: All offset settings are stored in volatile memory so they
have to be set every time the module is reset.
*/

#include "offset_cancellation.h"

void adjust_offset(MPU9255 &mpu)
{
  //set bandwidths to 5Hz to reduce the noise
  int16_t gX_offset = 0;//gyroscope X axis offset
  int16_t gY_offset = 0;//gyroscope Y axis offset
  int16_t gZ_offset = 0;//gyroscope Z axis offset

  int16_t aX_offset = 0;//accelerometer X axis offset
  int16_t aY_offset = 0;//accelerometer Y axis offset
  int16_t aZ_offset = 0;//accelerometer Z axis offset

  //update flags

  //gyroscope
  bool update_gX = true;
  bool update_gY = true;
  bool update_gZ = true;

  //accelerometer
  bool update_aX = true;
  bool update_aY = true;
  bool update_aZ = true;

  //discard the first reading
  mpu.read_acc();
  mpu.read_gyro();
  delay(10);

  while(1)//offset adjusting loop
  {
    mpu.read_acc();
    mpu.read_gyro();

    //-------- adjust accelerometer X axis offset ----------

    if(mpu.ax>0 && update_aX==true)//if X axis readings are greater than 0
    {
      aX_offset --;//decrement offset
    }


    if(mpu.ax<0 && update_aX==true)
    {
      aX_offset ++;//increment offset
    }

    //-------- adjust accelerometer Y axis offset ----------

    if(mpu.ay>0 && update_aY==true)//if X axis readings are greater than 0
    {
      aY_offset --;//decrement offset
    }

    if(mpu.ay<0 && update_aY==true)
    {
      aY_offset ++;//increment offset
    }

    //-------- adjust accelerometer Z axis offset ----------

    if(mpu.az>0 && update_aZ==true)//if X axis readings are greater than 0
    {
      aZ_offset --;//decrement offset
    }

    if(mpu.az<0 && update_aZ==true)
    {
      aZ_offset ++;//increment offset
    }

        //-------- adjust gyroscope X axis offset ----------

    if(mpu.gx>0 && update_gX==true)//if X axis readings are greater than 0
    {
      gX_offset --;//decrement offset
    }

    if(mpu.gx<0 && update_gX==true)
    {
      gX_offset ++;//increment offset
    }

    //-------- adjust gyroscope Y axis offset ----------

    if(mpu.gy>0 && update_gY==true)//if X axis readings are greater than 0
    {
      gY_offset --;//decrement offset
    }

    if(mpu.gy<0 && update_gY==true)
    {
      gY_offset ++;//increment offset
    }

    //-------- adjust gyroscope Z axis offset ----------

    if(mpu.gz>0 && update_gZ==true)//if X axis readings are greater than 0
    {
      gZ_offset --;//decrement offset
    }

    if(mpu.gz<0 && update_gZ==true)
    {
      gZ_offset ++;//increment offset
    }

    //set new offset
    if(update_gX==true)
    {
      mpu.set_gyro_offset(X_axis,gX_offset);
    }

    if(update_gY==true)
    {
      mpu.set_gyro_offset(Y_axis,gY_offset);
    }

    if(update_gZ==true)
    {
      mpu.set_gyro_offset(Z_axis,gZ_offset);
    }

    if(update_aX==true)
    {
      mpu.set_acc_offset(X_axis,aX_offset);
    }

    if(update_aY==true)
    {
      mpu.set_acc_offset(Y_axis,aY_offset);
    }

    if(update_aZ==true)
    {
      mpu.set_acc_offset(Z_axis,aZ_offset);
    }

    //------ Check if each axis is adjusted -----
    const short maximum_error = 5;//set maximum deviation to 5 LSB
    if((mpu.ax-maximum_error) <= 0)
    {

    }

    if((abs(mpu.ax)-maximum_error) <= 0)
    {
      update_aX = false;
    }

    if((abs(mpu.ay)-maximum_error) <= 0)
    {
      update_aY = false;
    }

    if((abs(mpu.az)-maximum_error) <= 0)
    {
      update_aZ = false;
    }

    if((abs(mpu.gx)-maximum_error) <= 0)
    {
      update_gX = false;
    }

    if((abs(mpu.gy)-maximum_error) <= 0)
    {
      update_gY = false;
    }

    if((abs(mpu.gz)-maximum_error) <= 0)
    {
      update_gZ = false;
    }


    //------ Adjust procedure end condition ------
    if(update_gX==false && update_gY==false && update_gZ==false && update_aX==false && update_aY==false && update_aZ==false)
    {
      break;
    }

    delay(10);
  }
}

